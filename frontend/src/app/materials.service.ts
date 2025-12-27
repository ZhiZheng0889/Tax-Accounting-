import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

export interface StudyMaterialListItem {
  category: string;
  title: string;
  relativePath: string;
}

export interface StudyMaterialContent {
  title: string;
  relativePath: string;
  markdown: string;
}

@Injectable({ providedIn: 'root' })
export class MaterialsService {
  constructor(private readonly http: HttpClient) {}

  listMaterials() {
    return this.http.get<StudyMaterialListItem[]>('/api/materials');
  }

  getContent(relativePath: string) {
    return this.http.get<StudyMaterialContent>('/api/materials/content', {
      params: { path: relativePath }
    });
  }
}
