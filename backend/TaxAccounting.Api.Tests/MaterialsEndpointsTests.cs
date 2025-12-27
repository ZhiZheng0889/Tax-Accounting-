using System.Net;
using System.Net.Http.Json;
using Microsoft.AspNetCore.Mvc.Testing;

namespace TaxAccounting.Api.Tests;

public sealed class MaterialsEndpointsTests : IClassFixture<WebApplicationFactory<Program>>
{
    private readonly WebApplicationFactory<Program> _factory;

    public MaterialsEndpointsTests(WebApplicationFactory<Program> factory)
    {
        _factory = factory;
    }

    [Fact]
    public async Task ListMaterials_ReturnsOkAndArray()
    {
        using var client = _factory.CreateClient();

        var response = await client.GetAsync("/api/materials");

        Assert.Equal(HttpStatusCode.OK, response.StatusCode);

        var items = await response.Content.ReadFromJsonAsync<List<StudyMaterialListItemDto>>();
        Assert.NotNull(items);
    }

    [Fact]
    public async Task Content_DisallowsPathTraversal()
    {
        using var client = _factory.CreateClient();

        var response = await client.GetAsync("/api/materials/content?path=../README.md");

        Assert.Equal(HttpStatusCode.BadRequest, response.StatusCode);
    }

    private sealed record StudyMaterialListItemDto(string Category, string Title, string RelativePath);
}
