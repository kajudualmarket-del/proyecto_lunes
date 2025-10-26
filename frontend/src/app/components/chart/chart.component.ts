import { Component, Input, OnChanges, SimpleChanges } from '@angular/core';
import { CommonModule } from '@angular/common';
import { NgChartsModule } from 'ng2-charts';
import { ChartData, ChartOptions } from 'chart.js';

@Component({
  selector: 'app-chart',
  templateUrl: './chart.component.html',
  styleUrls: ['./chart.component.css'],
  standalone: true,
  imports: [CommonModule, NgChartsModule]
})
export class ChartComponent implements OnChanges {
  // Cambiado de 'data' a 'chartData' para que coincida con el binding del AppComponent
  @Input() chartDataInput: any; // Recibe los datos desde AppComponent

  public chartData: ChartData<'bar'> = {
    labels: [],
    datasets: []
  };

  public chartOptions: ChartOptions<'bar'> = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: 'Estadísticas de Productos'
      }
    }
  };

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['chartDataInput'] && this.chartDataInput) {
      // Suponemos que chartDataInput es un arreglo de objetos { product: string, quantity: number }
      this.chartData.labels = this.chartDataInput.map((item: any) => item.product);
      this.chartData.datasets = [
        {
          label: 'Cantidad',
          data: this.chartDataInput.map((item: any) => item.quantity),
          backgroundColor: 'rgba(54, 162, 235, 0.6)',
          borderColor: 'rgba(54, 162, 235, 1)',
          borderWidth: 1
        }
      ];
    }
  }
}
