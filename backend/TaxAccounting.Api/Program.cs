var builder = WebApplication.CreateBuilder(args);

// Add services to the container.
// Learn more about configuring Swagger/OpenAPI at https://aka.ms/aspnetcore/swashbuckle
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

builder.Services.AddCors(options =>
{
    options.AddPolicy(
        name: "frontend-dev",
        policy => policy
            .WithOrigins("http://localhost:4200")
            .AllowAnyHeader()
            .AllowAnyMethod());
});

var app = builder.Build();

// Configure the HTTP request pipeline.
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.UseCors("frontend-dev");

app.UseHttpsRedirection();

var repoRoot = Path.GetFullPath(Path.Combine(builder.Environment.ContentRootPath, "..", ".."));
var noteRoots = new[]
{
    Path.Combine(repoRoot, "01-Tax"),
    Path.Combine(repoRoot, "02-Accounting"),
    Path.Combine(repoRoot, "03-References"),
};

app.MapGet("/api/health", () => Results.Ok(new { status = "ok" }))
    .WithName("Health")
    .WithOpenApi();

app.MapGet("/api/materials", () =>
    {
        var materials = noteRoots
            .Where(Directory.Exists)
            .SelectMany(root => Directory.EnumerateFiles(root, "*.md", SearchOption.AllDirectories))
            .Select(filePath =>
            {
                var relativePath = Path.GetRelativePath(repoRoot, filePath)
                    .Replace(Path.DirectorySeparatorChar, '/');

                var category = relativePath.Split('/', 2, StringSplitOptions.RemoveEmptyEntries).FirstOrDefault() ?? "";

                return new StudyMaterialListItem(
                    Category: category,
                    Title: Path.GetFileNameWithoutExtension(filePath),
                    RelativePath: relativePath);
            })
            .OrderBy(x => x.Category)
            .ThenBy(x => x.Title)
            .ToArray();

        return Results.Ok(materials);
    })
    .WithName("ListStudyMaterials")
    .WithOpenApi();

app.MapGet("/api/materials/content", (string path) =>
    {
        if (string.IsNullOrWhiteSpace(path))
        {
            return Results.BadRequest(new { error = "Missing 'path' query parameter." });
        }

        if (!path.EndsWith(".md", StringComparison.OrdinalIgnoreCase))
        {
            return Results.BadRequest(new { error = "Only .md files are supported." });
        }

        var combined = Path.GetFullPath(Path.Combine(repoRoot, path.Replace('/', Path.DirectorySeparatorChar)));
        if (!combined.StartsWith(repoRoot, StringComparison.OrdinalIgnoreCase))
        {
            return Results.BadRequest(new { error = "Invalid path." });
        }

        if (!File.Exists(combined))
        {
            return Results.NotFound(new { error = "File not found." });
        }

        var text = File.ReadAllText(combined);
        return Results.Ok(new StudyMaterialContent(
            Title: Path.GetFileNameWithoutExtension(combined),
            RelativePath: Path.GetRelativePath(repoRoot, combined).Replace(Path.DirectorySeparatorChar, '/'),
            Markdown: text));
    })
    .WithName("GetStudyMaterialContent")
    .WithOpenApi();

app.Run();

record StudyMaterialListItem(string Category, string Title, string RelativePath);

record StudyMaterialContent(string Title, string RelativePath, string Markdown);

public partial class Program { }
