import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { AppComponent } from './app.component';


@NgModule({
  imports: [
    BrowserModule,
    AppComponent // 👈 Importa el standalone component en bootstrap
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }