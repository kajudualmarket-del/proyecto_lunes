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
  @Input() chartDataInput: any; // Datos entrantes (varios formatos)

  // Tipado explícito del ViewChild para evitar problemas al llamar update()
  @ViewChild(BaseChartDirective, { static: false }) chart?: BaseChartDirective<'bar'>;

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

  ngOnChanges(changes: SimpleChanges): void {
    if (!changes['chartDataInput']) return;

    const incoming = this.chartDataInput ?? [];

    if (!Array.isArray(incoming)) {
      // No es un array: no hay datos válidos
      this.hasData = false;
      this.chartData = { labels: [], datasets: [] };
      return;
    }

    // Soportar varias formas: { producto, total } o { product, quantity } o { producto, cantidad }
    const products: string[] = incoming.map((item: any) => {
      return (item?.producto ?? item?.product ?? 'Desconocido') + '';
    });

    const quantities: number[] = incoming.map((item: any) => {
      const raw = item?.total ?? item?.quantity ?? item?.cantidad ?? 0;
      // Convertir de forma segura a número
      const n = (typeof raw === 'number') ? raw : Number(String(raw).replace(',', '.'));
      return Number.isFinite(n) ? Math.round(n) : 0;
    });

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
          // eslint-disable-next-line @typescript-eslint/ban-ts-comment
          // @ts-ignore - propiedad usada por ng2-charts for hover style
          hoverBackgroundColor: 'rgba(75, 192, 192, 0.8)',
        }
      ]
    };

    // Actualiza el chart de forma segura (si ya está montado)
    if (this.chart && typeof this.chart.update === 'function') {
      try {
        this.chart.update();
      } catch (err) {
        // si falla la actualización no rompemos la app — dejamos los datos listos para dibujar
        // y lo registramos en consola para debugging.
        // No borro nada ni toco lógica ajena — solo prevengo el crash.
        // eslint-disable-next-line no-console
        console.warn('Error al actualizar chart:', err);
      }
    }
  }
}
