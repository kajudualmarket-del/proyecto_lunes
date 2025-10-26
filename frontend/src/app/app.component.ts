import { Component } from '@angular/core';
import { UploadComponent } from './components/upload/upload.component';
import { ChartComponent } from './components/chart/chart.component';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css'],
  standalone: true,
  imports: [UploadComponent, ChartComponent] // Importamos los componentes necesarios
})
export class AppComponent {
  title = 'trabajo-lunes';

  // No ponemos datos de ejemplo, el chart tomará los datos del UploadComponent
}
