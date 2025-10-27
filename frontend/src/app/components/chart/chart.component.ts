import { Component, Input, OnChanges, SimpleChanges, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { NgChartsModule, BaseChartDirective } from 'ng2-charts';
import { ChartData, ChartOptions } from 'chart.js';

@Component({
  selector: 'app-chart',
  templateUrl: './chart.component.html',
  styleUrls: ['./chart.component.css'],
  standalone: true,
  imports: [CommonModule, NgChartsModule]
})
export class ChartComponent implements OnChanges {
  @Input() chartDataInput: any; // 🔹 Datos que llegan del padre

  // 🔹 Referencia directa al gráfico (para actualizar sin duplicar)
  @ViewChild(BaseChartDirective) chart?: BaseChartDirective;

  // 🔹 Controla cuándo mostrar el gráfico
  public hasData = false;

  public chartData: ChartData<'bar'> = {
    labels: [],
    datasets: []
  };

  public chartOptions: ChartOptions<'bar'> = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
        labels: {
          color: '#333',
          font: { size: 13, family: 'Poppins, sans-serif' }
        }
      },
      title: {
        display: true,
        text: 'Estadísticas de Productos',
        color: '#2a3f54',
        font: { size: 18, weight: 'bold', family: 'Poppins, sans-serif' }
      }
    },
    scales: {
      x: {
        ticks: { color: '#555' },
        grid: { display: false }
      },
      y: {
        ticks: { color: '#555' },
        grid: { color: '#e0e0e0' }
      }
    },
    animation: { duration: 1000, easing: 'easeOutQuart' }
  };

  // 🔹 Detecta cambios en los datos
  ngOnChanges(changes: SimpleChanges): void {
    if (changes['chartDataInput'] && Array.isArray(this.chartDataInput)) {
      const products = this.chartDataInput.map((item: any) => item.product ?? 'Desconocido');
      const quantities = this.chartDataInput.map((item: any) => item.quantity ?? 0);

      // Muestra el gráfico solo si hay datos válidos
      this.hasData = products.length > 0 && quantities.some(q => q > 0);

      this.chartData = {
        labels: products,
        datasets: [
          {
            label: 'Cantidad',
            data: quantities,
            backgroundColor: 'rgba(54, 162, 235, 0.6)',
            borderColor: 'rgba(54, 162, 235, 1)',
            borderWidth: 1,
            borderRadius: 6,
            hoverBackgroundColor: 'rgba(75, 192, 192, 0.8)',
          }
        ]
      };

      // 🔹 Actualiza el gráfico existente sin duplicarlo
      if (this.chart) {
        this.chart.update();
      }
    }
  }
}
