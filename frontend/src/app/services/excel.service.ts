import { Injectable } from '@angular/core';
import { HttpClient, HttpEvent, HttpRequest } from '@angular/common/http';
import { Observable, BehaviorSubject, map } from 'rxjs';
import { ExcelFile } from '../models/excel-file.model';
import { ExcelData } from '../models/excel-data.model';

@Injectable({
  providedIn: 'root'
})
export class ExcelService {
  private baseUrl = 'http://localhost:8009'; // ⚠️ Ajusta el puerto si es distinto

  private chartDataSubject = new BehaviorSubject<ExcelData[]>([]);
  chartData$ = this.chartDataSubject.asObservable();

  constructor(private http: HttpClient) {}

  uploadExcel(file: File): Observable<HttpEvent<any>> {
    const formData: FormData = new FormData();
    formData.append('file', file, file.name);

    const req = new HttpRequest('POST', `${this.baseUrl}/files/upload`, formData, {
      reportProgress: true,
      responseType: 'json'
    });
    return this.http.request(req);
  }

  getFiles(): Observable<ExcelFile[]> {
    return this.http.get<any>(`${this.baseUrl}/files`).pipe(
      map((response) => response?.data?.files || [])
    );
  }

  getExcelPreview(id: number): Observable<ExcelData[]> {
    return this.http.get<ExcelData[]>(`${this.baseUrl}/files/preview/${id}`);
  }

  insertExcelData(id: number): Observable<any> {
    return this.http.post(`${this.baseUrl}/files/insert/${id}`, {});
  }

  deleteFile(id: number): Observable<any> {
    return this.http.delete(`${this.baseUrl}/files/${id}`);
  }

  // ✅ Devuelve directamente el array limpio del backend (data.chart)
  getChartData(): Observable<ExcelData[]> {
    return this.http.get<any>(`${this.baseUrl}/files/chart`).pipe(
      map((response) => response?.data?.chart || [])
    );
  }

  setChartData(data: ExcelData[]) {
    this.chartDataSubject.next(data);
  }

  fetchChartData() {
    this.getChartData().subscribe({
      next: (data: ExcelData[]) => this.setChartData(data),
      error: (err) => console.error('Error al obtener datos del gráfico:', err)
    });
  }
}
