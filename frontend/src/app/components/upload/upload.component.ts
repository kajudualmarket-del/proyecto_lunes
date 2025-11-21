import { Component } from '@angular/core';
import { HttpEventType } from '@angular/common/http';
import { ExcelService } from '../../services/excel.service';
import { ExcelFile } from '../../models/excel-file.model';
import { CommonModule } from '@angular/common';
import { ChartComponent } from '../chart/chart.component';

@Component({
  selector: 'app-upload',
  templateUrl: './upload.component.html',
  styleUrls: ['./upload.component.css'],
  imports: [CommonModule, ChartComponent],
  standalone: true
})
export class UploadComponent {
  selectedFile: File | null = null;
  uploadProgress = 0;
  message = '';
  files: ExcelFile[] = [];
  previewData: any = null;
  chartData: any = null;
  emptySheets: string[] = [];
  inserting = false;

  Object = Object;

  constructor(private excelService: ExcelService) {}

  ngOnInit(): void {
    this.loadFiles();
  }

  onFileSelected(event: any): void {
    const file = event.target.files[0];
    if (file && (file.name.endsWith('.xls') || file.name.endsWith('.xlsx'))) {
      this.selectedFile = file;
    } else {
      alert('Solo se permiten archivos .xls o .xlsx');
    }
  }

  uploadFile(): void {
    if (!this.selectedFile) {
      alert('Seleccione un archivo primero');
      return;
    }

    this.previewData = null;
    this.chartData = null;
    this.uploadProgress = 0;
    this.message = '';

    this.excelService.uploadExcel(this.selectedFile).subscribe({
      next: (event) => {
        if (event.type === HttpEventType.UploadProgress && event.total) {
          this.uploadProgress = Math.round((100 * event.loaded) / event.total);
        } else if (event.type === HttpEventType.Response) {
          this.message = '✅ Archivo subido correctamente';
          this.uploadProgress = 100;
          this.loadFiles();
        }
      },
      error: () => {
        this.message = '❌ Error al subir archivo';
      }
    });
  }

  loadFiles(): void {
    this.excelService.getFiles().subscribe({
      next: (data) => (this.files = data),
      error: () => alert('Error al cargar archivos')
    });
  }

  showPreview(fileId: number): void {
    this.chartData = null;
    this.previewData = null;
    this.emptySheets = [];

    this.excelService.getExcelPreview(fileId).subscribe({
      next: (data) => {
        this.previewData = data;
        if (Array.isArray(data)) {
          data.forEach((sheet: any) => {
            if (!sheet.datos || sheet.datos.length === 0) {
              this.emptySheets.push(sheet.nombre);
            }
          });
        }
        if (this.emptySheets.length > 0) {
          alert(`⚠️ Las siguientes hojas están vacías:\n${this.emptySheets.join(', ')}`);
        }
      },
      error: () => alert('Error al obtener previsualización')
    });
  }

  insertData(fileId: number): void {
    if (this.inserting) return;
    this.inserting = true;
    this.uploadProgress = 0;

    const button = document.activeElement as HTMLElement;
    button.classList.add('loading');

    const interval = setInterval(() => {
      if (this.uploadProgress < 95) this.uploadProgress += 5;
      else clearInterval(interval);
    }, 100);

    this.excelService.insertExcelData(fileId).subscribe({
      next: () => {
        this.uploadProgress = 100;
        this.inserting = false;
        button.classList.remove('loading');
        alert('✅ Datos insertados correctamente');
        this.fetchChartData();
      },
      error: () => {
        alert('❌ Error al insertar datos');
        this.inserting = false;
        button.classList.remove('loading');
      }
    });
  }

  deleteFile(id: number): void {
    if (confirm('¿Desea eliminar este archivo?')) {
      this.excelService.deleteFile(id).subscribe({
        next: () => {
          this.loadFiles();
          this.fetchChartData();
        },
        error: () => alert('Error al eliminar archivo')
      });
    }
  }

  fetchChartData(): void {
    this.excelService.getChartData().subscribe({
      next: (chart) => (this.chartData = chart || []),
      error: () => console.error('Error al obtener datos del gráfico')
    });
  }
}
