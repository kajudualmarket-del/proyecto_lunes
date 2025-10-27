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

  // === 🌙 NUEVO: Control del modo oscuro ===
  isDarkTheme = false;

  toggleTheme() {
    this.isDarkTheme = !this.isDarkTheme;
    const body = document.body;
    if (this.isDarkTheme) {
      body.classList.add('dark-theme');
    } else {
      body.classList.remove('dark-theme');
    }
  }

  // No tocamos nada de tu lógica existente
}
