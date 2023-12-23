# Simple Homebroker Data API (SHDA)
## Overview
Simple Homebroker Data API (SHDA) es una API para conectar cualquier script de python al mercado para recibir información de cotizaciones en tiempo real. Fue desarrollada en conjunto por Marcelo Colom, [St1tch](https://twitter.com/St1tch_BL) y [Franco Lamas](https://www.linkedin.com/in/franco-lamas/), ademas utliza parte del codigo de [pyhomebroker](https://github.com/crapher/pyhomebroker) desarrollada por [Diego Degese](https://twitter.com/diegodegese).

**Necesita una cuenta en uno de los [Brokers Soportados](#Brokers-Soportados).**

# Uso
## Inicialización

    import SHDA
    hb=SHDA.SHDA(broker,dni,user,password)

## Datos de mercados
| Plazo |Parametro|
| ------------ | :------------: |
| 48hs |"48hs"|
| 24hs |"24hs"|
| CI |"spot"|

### Cotizaciones de Bonos

    hb.get_bonds("48hs")

### Cotizaciones de Letras

    hb.get_short_term_bonds("48hs")

### Cotizaciones de Bonos Coporativos
    hb.get_corporate_bonds("48hs")

### Cotizaciones del Panel MERVAL

    hb.get_bluechips("48hs")

### Cotizaciones del Panel General

    hb.get_galpones("48hs")

### Cotizaciones de CEDEAR

    hb.get_cedears("48hs")

### Cotizaciones de los índices 

    hb.get_MERVAL()
    
### Cotizaciones de opciones

    hb.get_options()

### Cotizaciones de Favoritos
Esta opcion no necesita parametros.

    hb.get_personal_portfolio()

### Tenencias
De momento no obtiene el numero de cuenta de manera automatica por lo que hay que pasarlo como parametro.

    hb.account(nro comitente)    


## Brokers Soportados

| Broker|Byma Id|
| ------------ | :------------: |
|Buenos Aires Valores S.A.|12|
|Proficio Investment S.A.|20|
|Tomar Inversiones S.A.|81|
|Bell Investments S.A.|88|
|RIG Valores S.A.|91|
|Soluciones Financieras S.A.|94|
|Maestro y Huerres S.A.|127|
|Bolsa de Comercio del Chaco|153|
|Prosecurities S.A.|164|
|Servente y Cia. S.A.|186|
|Alfy Inversiones S.A.|201|
|Invertir en Bolsa S.A.|203|
|Futuro Bursátil S.A.|209|
|Sailing S.A.|233|
|Negocios Financieros y Bursátiles S.A. (Cocos Capital)|265|
|Veta Capital S.A.|284|
# Instalacion

Instalación vía pip.

    pip install SHDA --upgrade --no-cache-dir
    
 
 ## Atribuciones y marcas

Home Broker una marca registrada de Estudio Gallo S.R.L.
Agradecemos a Diego Degese por crear y compartir [pyhomebroker](https://github.com/crapher/pyhomebroker)

## To-do List
- Corregir nombres de columnas de Tenencias.



# DISCLAIMER

La información es mostrada “tal cual es”, puede ser incorrecta o contener errores, eso es responsabilidad de cada sitio. No somos responsables por el uso indebido de los Scripts.
