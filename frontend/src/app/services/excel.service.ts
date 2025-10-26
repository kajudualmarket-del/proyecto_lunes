import { Injectable } from '@angular/core';
import { HttpClient, HttpEvent, HttpRequest } from '@angular/common/http';
import { Observable, BehaviorSubject } from 'rxjs';
import { ExcelFile } from '../models/excel-file.model';
import { ExcelData } from '../models/excel-data.model';

@Injectable({
  providedIn: 'root'
})
export class ExcelService {
  private baseUrl = 'http://localhost:8009'; // Backend FastAPI

  // NUEVO: BehaviorSubject para los datos del chart
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
    return this.http.get<ExcelFile[]>(`${this.baseUrl}/files`);
  }

  getExcelPreview(id: number): Observable<ExcelData[]> {
    return this.http.get<ExcelData[]>(`${this.baseUrl}/files/${id}`);
  }

  insertExcelData(id: number): Observable<any> {
    return this.http.post(`${this.baseUrl}/files/insert/${id}`, {});
  }

  deleteFile(id: number): Observable<any> {
    return this.http.delete(`${this.baseUrl}/files/${id}`);
  }

  getChartData(): Observable<any> {
    return this.http.get(`${this.baseUrl}/files/chart`);
  }

  // NUEVO: actualizar chartData
  setChartData(data: ExcelData[]) {
    this.chartDataSubject.next(data);
  }

  // NUEVO: obtener datos y actualizar automáticamente el BehaviorSubject
  fetchChartData() {
    this.getChartData().subscribe((data: ExcelData[]) => {
      this.setChartData(data);
    });
  }
}
