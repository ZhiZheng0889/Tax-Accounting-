import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MaterialsService, StudyMaterialContent, StudyMaterialListItem } from './materials.service';

@Component({
  selector: 'app-root',
  imports: [CommonModule],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App {
  protected loading = true;
  protected error: string | null = null;
  protected materials: StudyMaterialListItem[] = [];
  protected selected: StudyMaterialContent | null = null;

  constructor(private readonly materialsService: MaterialsService) {
    this.materialsService.listMaterials().subscribe({
      next: items => {
        this.materials = items;
        this.loading = false;
      },
      error: err => {
        this.error = err?.message ?? 'Failed to load materials.';
        this.loading = false;
      }
    });
  }

  protected open(item: StudyMaterialListItem) {
    this.selected = null;
    this.materialsService.getContent(item.relativePath).subscribe({
      next: content => {
        this.selected = content;
      },
      error: err => {
        this.error = err?.message ?? 'Failed to load content.';
      }
    });
  }
}
