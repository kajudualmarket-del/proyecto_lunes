import { Component } from '@angular/core';
import { HttpEventType } from '@angular/common/http';
import { ExcelService } from '../../services/excel.service';
import { ExcelFile } from '../../models/excel-file.model';
import { CommonModule } from '@angular/common';
import { ChartComponent } from '../chart/chart.component'; // Importa el chart

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

  // NUEVO: datos para el gráfico
  chartData: any = null;

  constructor(private excelService: ExcelService) {}

  ngOnInit(): void {
    this.loadFiles();
    this.fetchChartData(); // NUEVO: carga inicial del gráfico
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

    this.excelService.uploadExcel(this.selectedFile).subscribe({
      next: (event) => {
        if (event.type === HttpEventType.UploadProgress && event.total) {
          this.uploadProgress = Math.round((100 * event.loaded) / event.total);
        } else if (event.type === HttpEventType.Response) {
          this.message = 'Archivo subido correctamente';
          this.uploadProgress = 100;
          this.loadFiles();

          // NUEVO: actualizar gráfico después de subir
          this.fetchChartData();
        }
      },
      error: () => {
        this.message = 'Error al subir archivo';
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
    this.excelService.getExcelPreview(fileId).subscribe({
      next: (data) => (this.previewData = data),
      error: () => alert('Error al obtener previsualización')
    });
  }

  insertData(fileId: number): void {
    this.uploadProgress = 0;
    const interval = setInterval(() => {
      if (this.uploadProgress < 100) this.uploadProgress += 5;
      else clearInterval(interval);
    }, 100);

    this.excelService.insertExcelData(fileId).subscribe({
      next: () => {
        alert('Datos insertados correctamente');
        this.uploadProgress = 100;

        // NUEVO: actualizar gráfico después de insertar
        this.fetchChartData();
      },
      error: () => alert('Error al insertar datos')
    });
  }

  deleteFile(id: number): void {
    if (confirm('¿Desea eliminar este archivo?')) {
      this.excelService.deleteFile(id).subscribe({
        next: () => {
          this.loadFiles();
          // NUEVO: actualizar gráfico después de eliminar
          this.fetchChartData();
        },
        error: () => alert('Error al eliminar archivo')
      });
    }
  }

  // NUEVO: método para obtener datos del gráfico
  fetchChartData(): void {
    this.excelService.getChartData().subscribe({
      next: (data) => {
        this.chartData = data;
      },
      error: () => console.error('Error al obtener datos del gráfico')
    });
  }
}
