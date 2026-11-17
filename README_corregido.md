# inversor_minimo_XT018
Tarea_1_Introducción al diseño de circuitos integrados

> **Estado del informe:** esta copia conserva los resultados ya disponibles y separa los análisis complementarios de los entregables que todavía requieren simulaciones. Los pendientes están marcados explícitamente; no se deben considerar resultados completos hasta añadir sus datos y gráficas.

## Caracterización preliminar del proceso XT018 (insumo para la Parte 2)

### Curvas I-V de transistores mínimos
#### Fórmula de la resistencia cuando el transistor esta saturado
$$R_{eff} = \frac{3In(2)}{4} \frac{V_{DD}}{I_{sat}}  \quad(1)$$ 

#### Fórmula de la resistencia cuando el transistor esta en transición
$$R_{eff} = \frac{V_{DD}}{I_{H}+I_{L}}  \quad(2)$$
\
\
Los valores para los siguientes cáculos se tomaron de los parámetros para transistores 1.8V (ne,pe) de un proceso XT018 - 0.18 µm. Además para los cáculos realizados, se desprecia $I_{L}$, ya que su valor en comparación con otras corrientes en el circuitos es muy pequeña. Para calcular la resistencia del transistor completo se escaló la corriente por unidad de ancho usando el ancho del transistor.

### Cáculos para transistor NMOS
A continuación se presentan los cálculo con la ecuación (1).
$$R_{eff} = \frac{3In(2)}{4} \frac{1.8V}{475 \times 10^{-6} A/{\micro m} \cdot 0.36{\micro m}} \approx 5.5 k\ohm $$  

Ahora con la ecuación (2).
$$R_{eff} = \frac{1.8V} {(475 \times 10^{-6} A/{\micro m}) \cdot 0.36{\micro m}} \approx 10.6 k\ohm$$
\
Para determinar la resistencia unitaria de un transistor NMOS para el proceso XT018 - 0.18 µm se realiza de la siguiente forma.
$$R_{nueff} = \frac{1.8V} {(475 \times 10^{-6} A/{\micro m})} \approx 3.8 k\ohm * {\micro m}$$

Estos valores difieren ya que la ecuación que usa la corriente de saturación solo funcionaría para transistores digitalizados que operen siempre en saturación de velocidad.
### Análisis empírico
Para determinar de forma empírica el valor de resistencia del transistor NMOS para el proceso XT018 se montó el deck `nmos_test.sp` y luego se exportaron en un archivo .csv para gráficarlas en python y se obtuvieron las siguientes gráficas.

![NMOS_Ids_Vds](https://github.com/DJosueMM/inversor_minimo_XH018/assets/125601912/79e5fc9f-8c60-49d7-87f3-55c9065d06c1)

![NMOS_Ids_Vgs](https://github.com/DJosueMM/inversor_minimo_XH018/assets/125601912/2201089d-fc23-433e-aa93-48ea43aab2c2)


Para determinar la resistencia mediante la ecuación (1) se utilizó la gráfica de la función de transferencia de NMOS, con esta se aproximo el valor de $I_{sat}$ y se realizó el cálculo que se presenta a continuación. 

$$R_{eff} =\frac{3In(2)}{4} \frac{1.8V} {213.7 \micro A} \approx 4.4 k\ohm$$

Con ayuda de la gráfica de la curva característica del transistor NMOS se extrajeron los datos de $I_H$ e $I_L$, estos dieron como resultado $199 \micro A$ y $29.07 \micro A$ respectivamente, una vez obtenidos los datos se procedió a resolver la ecuación (2), el resultado se presenta a continuación. 

$$R_{eff} =  \frac{1.8V}{199 \micro A  + 29.07 \micro A}  \approx 7.9 k\ohm $$  

Con los valores obtenido anteriormente se determinó la resistencia unitaria para un transistor NMOS, el cual se obtuvo el siguiente resultado. 
$$R_{nueff} = \frac{7.9 k\ohm} {{0.36 \micro m}} \approx 22 k\ohm/\micro m$$


### Cáculos para transistor PMOS
A continuación se presentan los cálculo con la ecuación (1).
$$R_{eff} = \frac{3In(2)}{4} \frac{1.8V}{170 \times 10^{-6} A/{\micro m} \cdot 0.72{\micro m}} \approx 7.7 k\ohm $$ 

Ahora con la ecuación (2).
$$R_{eff} = \frac{1.8V} {(170 \times 10^{-6} A/{\micro m}) \cdot 0.72{\micro m}} \approx 14.7 k\ohm$$
\
El deck de prueba usa el valor por defecto `P=8` y una escala de 90 nm, por lo que el ancho PMOS es 0.72 µm. Para determinar la resistencia unitaria de ese transistor:
$$R_{pueff} = \frac{1.8V} {(170 \times 10^{-6} A/{\micro m})} \approx 10.6 k\ohm * {\micro m}$$

### Análisis empírico
Una manera muy parecida se realizó para determinarlo los valores de resistencia de PMOS pero en este caso se uso el deck `pmos_test.sp`, para posteriomente realizar el mismo procedimiento que el nmos, a continuación se presenta las gráficas y los cálculos realizados. 

![PMOS_Ids_Vds](https://github.com/DJosueMM/inversor_minimo_XH018/assets/125601912/1cccd635-e6b7-4593-b39b-c3e37863f585)

![PMOS_Ids_Vgs](https://github.com/DJosueMM/inversor_minimo_XH018/assets/125601912/81328b36-2d41-40da-9319-c40e7a9983ee)

Primero se presenta los cálculos con la ecuación (1).
$$R_{eff} =\frac{3In(2)}{4} \frac{1.8V} {180.5 \micro A} \approx 5.2 k\ohm$$

Ahora con la ecuación (2) donde con ayuda de la gráfica se determinó que $I_H=102\micro A$ e $I_L=13.01\micro A$.

$$R_{eff} =  \frac{1.8V}{102 \micro A + 13.01 \micro A}  \approx 15.65 k\ohm $$  

Para determinar la resistencia unitaria de un transistor PMOS para el proceso XT018 - 0.18 µm se realiza de la siguiente forma.
$$R_{pueff} = \frac{15.65 k\ohm} {{0.72 \micro m}} \approx 21.74 k\ohm/\micro m$$
\
\
Al comparar los datos obtenidos con los valores teóricos, se aprecian diferencias de alrededor de $4 k\ohm$ máximo. Esto se debe a que el analísis teórico realizado se cálculo con valor de $W/L= (10/0.18) \micro m/\micro m$, ya que el parámetros porporcionados para la tecnología XT018 mostraban ese valor, lo cual implica un gran impacto en los valores debido a que no se considera el valor mínimo de ancho necesario para esta tecngología que es $0.36 \micro m$. Por lo que, al tenes este parámetro diferente al requerido, se puede considerar que los valores teóricos generados tiene una pequeña discrepancia con respecto a los datos experimentales.  

Tambien se comprueba que la resistencia efectiva del PMOS es aproximadamente 2 veces la del NMOS.

> **Pendiente para completar 2.a:** la consigna solicita extraer la resistencia promedio durante la descarga de un capacitor suficientemente grande en el intervalo \(V_{DD}\) a \(V_{DD}/2\). Las curvas I-V y estimaciones de esta sección son caracterización complementaria y no sustituyen ese procedimiento.

### Estimación preliminar de capacitancia de compuerta y constante RC (insumo para Parte 2.b)
Los valores para los siguientes cáculos se tomaron de los parámetros para transistores 1.8V (ne,pe) de un proceso XT018 - 0.18 µm.

#### Fórmula de la capacitancia parásita si se considera pesimista 
$$C_{gs} = W_{dib} L_{dib}C_{ox} +  W_{dib}  C_{ov}  \quad(3)$$

#### Fórmula de la constante RC ($\tau$) 
$$\tau = 3R_{n}C  \quad(4)$$

$$\tau = (3/2) R_{p}C  \quad(5)$$

### Transistor NMOS
#### Cálculo de la capacitancia 
A continuación se presentan los cálculo con la ecuación (3).
$$C_{gn} = 0.36\micro m \cdot 0.18\micro m \cdot 8.46 fF/\micro{m}^{2} +  0.36\micro m \cdot 0.33 fF/\micro m $$
$$C_{gn} \approx 0.67 fF$$

#### Cálculo de la constante RC ($\tau$)
Para determinar la constante RC para el transistor NMOS se utlizó la ecuación (4), el desarollo de la misma se presenta a continuación.
$$\tau = 3 \cdot 10.6 k\ohm \cdot 0.67 fF = 21.31 ps$$


### Transistor PMOS
#### Cálculo de la capacitancia 
A continuación se presentan los cálculo con la ecuación (3).
$$C_{gp} = 0.72\micro m \cdot 0.18\micro m \cdot 8.91 fF/\micro{m}^{2} +  0.72\micro m \cdot 0.32 fF/\micro m $$
$$C_{gp} \approx 1.39 fF$$

#### Cálculo de la constante RC ($\tau$)
Para determinar la constante RC para el transistor PMOS se utlizó la ecuación (5), el desarollo de la misma se presenta a continuación.
$$\tau = 3/2 \cdot 14.7 k\ohm \cdot 1.39fF = 30.64 ps$$

> **Pendiente para completar 2.b:** incluir capacitancias de difusión, extracción de resistencias desde retardos SPICE y la iteración indicada en la consigna usando primero \(W_P/W_N=2\) y luego la relación obtenida. Los valores anteriores son estimaciones preliminares de capacitancia de compuerta.


## Parte 1. Diseño y caracterización del inversor CMOS mínimo
### Parte 1.a. Dimensionamiento y VTC del inversor

#### Inversor de tamaño mínimo 

Se diseñó a nivel de esquemático el inversor que se muestra en la siguiente figura:

![Esquemático del inversor](https://github.com/DJosueMM/inversor_minimo_XH018/blob/main/Imagenes/sch_inversor.png)

Este cuenta con un NMOS de tamaño mínimo permitido por las reglas escalables con contactos en las difusiones para la tecnología utilizada. Teniendo un valor de lambda de 90 nm, la expresión del transistor mínimo 4/2 lambda resulta en un ancho de NMOS de 360 nm.

Para obtener un inversor sin sesgo con márgenes de ruido totalmente simétricos, se debe cumplir que al tener VDD/2 en la entrada, su salida sea también VDD/2. Esto implica que los parámetros Beta tendrán una relación Bp/Bn = 1. Para lograr esto, se diseñó el deck de HSPICE `inverter_transfer.sp`, donde se obtienen las funciones de transferencia para diferentes relaciones de anchos de transistor P/N. Al simular estos datos, se obtuvo la siguiente gráfica:

![Función de transferencia del inversor](https://github.com/DJosueMM/inversor_minimo_XH018/blob/main/Imagenes/tf_inv_ra.png)

#### Dimensionamiento analítico de primer orden

Se fija \(V_{DD}=1.8\,\mathrm{V}\), \(V_M=V_{DD}/2=0.9\,\mathrm{V}\), \(W_N=0.36\,\mu\mathrm{m}\) y \(L=0.18\,\mu\mathrm{m}\). Para el punto \(V_{in}=V_{out}=V_M\), las magnitudes de las tensiones de sobreexcitación son:

$$V_{OV,n}=V_M-V_{TN}=0.9-0.58=0.32\,\mathrm{V}$$
$$V_{OV,p}=V_{DD}-V_M-|V_{TP}|=0.9-0.65=0.25\,\mathrm{V}$$

Los valores de umbral se toman de la fila de canal mínimo \(W/L=10/0.18\) del documento de parámetros de primer orden [4]. Para ambos transistores, \(V_{DS}=V_{SD}=0.9\,\mathrm{V}\), mayor que sus respectivos sobrevoltajes. Esto satisface la condición de saturación del modelo de canal largo en el punto de conmutación, aunque no prueba por sí solo que el transistor esté en saturación de velocidad.

Como el canal dibujado es mínimo (\(L=0.18\,\mu\mathrm{m}\)), no se adopta el modelo cuadrático de canal largo como predicción principal: el documento [4] advierte que es probable la saturación de velocidad, al menos en NMOS, y que \(K'_L\) está medido en la región lineal para transistores largos. Se usa, por tanto, una aproximación de corriente limitada por velocidad, lineal con el sobrevoltaje:

$$\frac{I_D}{W}\approx \frac{I_{ON}}{V_{DD}-V_T}V_{OV}$$

Esta extrapolación usa \(I_{ON}\) por unidad de ancho medido a \(V_{GS}=V_{DS}=1.8\,\mathrm{V}\); no es un modelo BSIM ni una medida a \(V_M\). Con \(I_{ON,n}=475\,\mu\mathrm{A}/\mu\mathrm{m}\) e \(I_{ON,p}=170\,\mu\mathrm{A}/\mu\mathrm{m}\):

$$\left.\frac{I_n}{W_n}\right|_{V_M}\approx475\frac{0.32}{1.8-0.58}=124.6\,\mu\mathrm{A}/\mu\mathrm{m}$$
$$\left.\frac{|I_p|}{W_p}\right|_{V_M}\approx170\frac{0.25}{1.8-0.65}=37.0\,\mu\mathrm{A}/\mu\mathrm{m}$$

Imponiendo \(I_n=|I_p|\) en \(V_M\), se obtiene:

$$\frac{W_p}{W_n}\approx\frac{(I_n/W_n)}{(|I_p|/W_p)}=\frac{124.6}{37.0}=3.37$$
$$W_p\approx3.37(0.36\,\mu\mathrm{m})=1.21\,\mu\mathrm{m}\approx13.5\lambda$$

Como contraste, el modelo cuadrático de canal largo daría \(W_p/W_n=(K'_n/K'_p)(V_{OV,n}/V_{OV,p})^2=(256/52)(0.32/0.25)^2\approx8.07\), o \(W_p\approx2.91\,\mu\mathrm{m}\). Se reporta solo como comparación: \(K'_L\) corresponde a la región lineal y los valores son de canal largo, por lo que su uso con \(L=0.18\,\mu\mathrm{m}\) no representa bien el régimen probable del NMOS mínimo.

La barrida discreta de VTC reporta una relación aproximada de 3.1:1. Es cercana a la estimación de primer orden 3.37:1 (diferencia aproximada del 9% respecto a 3.1), lo cual es razonable dada la extrapolación de \(I_{ON}\), la cuantización de la barrida y los efectos de canal corto/parásitos no incluidos. La simulación es la que debe determinar el valor final.

En cuanto a la corriente de cortocircuito, que ocurre cuando ambos transistores están encendidos en el punto donde Vout = VDD/2, se obtuvo la siguiente gráfica de corriente de cortocircuito en función de la relación P/N:

![Corriente de cortocircuito](https://github.com/DJosueMM/inversor_minimo_XH018/blob/main/Imagenes/FO4_opt_isc.png)

El archivo de datos reporta un valor de 0.8973 para una relación P/N de 3:1. La unidad de ese valor debe verificarse contra la configuración/exportación de HSPICE antes de reportarla; no se afirma aquí que sean amperios.

> **Pendiente para completar 1.a:** superponer la curva de SPICE con la VTC del modelo analítico usando la relación calculada, explicar las diferencias observadas y confirmar en el resultado de HSPICE la unidad de la corriente de cortocircuito.

Los análisis anteriores se realizaron para una esquina de variabilidad del proceso "tm typical medium", que representa el comportamiento neutral. No obstante, se pueden realizar análisis en otras esquinas de variabilidad donde se sesga el inversor, haciendo más rápido el PMOS o el NMOS. Se llevó a cabo este análisis en las siguientes esquinas:

- WP: worst case power; NMOS rápido y PMOS rápido
- WS: worst case speed; NMOS lento y PMOS lento
- WO: worst case one; NMOS rápido y PMOS lento
- WZ: worst case zero; NMOS lento y PMOS rápido

Se simuló el inversor para cada esquina de variabilidad para obtener los tiempos de transición:

![inv_corners](https://github.com/DJosueMM/inversor_minimo_XH018/blob/main/Imagenes/transient_inv_esquinas.png)

De estos datos, se obtuvieron los respectivos tiempos de propagación de subida y de caída para cada esquina:

![Esquinas de variabilidad](https://github.com/DJosueMM/inversor_minimo_XH018/blob/main/Imagenes/corners_const.png)


### Análisis complementario: cadena FO4 y optimización de retardos

#### FO4

Se montó el FO4 que propone el libro [1], este se encuentra en `fo4_ratios.sp`. Con una ratio P/N de 2:1 se obtuvieron las señales en cada etapa del FO4:

Se obtuvo un tpdr = 80.76 ps, un tpdf = 70.34 ps y un tpd = 75.55 ps.

![fo4](https://github.com/DJosueMM/inversor_minimo_XH018/blob/main/Imagenes/FO4.png)

Este análisis de una cadena FO4 es complementario; por sí solo no reemplaza el caso de la consigna 1.b, que considera un inversor manejando una carga similar a sí mismo.

#### Estimación analítica con carga de un inversor idéntico

Se interpreta “carga similar a sí mismo” como un inversor idéntico conectado a la salida. Se conserva \(W_N=0.36\,\mu\mathrm{m}\) y se dimensiona \(W_P\) para que los retardos de subida y bajada sean iguales. En el modelo RC de primer orden:

$$t_{pHL}\approx0.69R_nC_L,\qquad t_{pLH}\approx0.69R_pC_L$$

Ambas transiciones ven la misma capacitancia de carga, por lo que la condición de simetría es \(R_n=R_p\), equivalente a igualar las corrientes de NMOS y PMOS en el punto de conmutación. Con la aproximación de saturación de velocidad adoptada en 1.a resulta \(W_P/W_N\approx3.37\), \(W_P\approx1.21\,\mu\mathrm{m}\). Bajo la restricción de retardos iguales y con \(W_N\) fijado al mínimo, esta relación fija el tamaño de PMOS y, por tanto, el retardo estimado.

Para estimar la carga se usa el modelo pesimista de capacitancias de [4], \(C_g=W_{dib}L_{dib}C_{ox}+W_{dib}C_{ov}\), y la aproximación del mismo documento \(C_{db}=C_{sb}=C_g\). Sin capacitancia de cableado:

$$C_{g,n}=0.36(0.18)(8.46)+0.36(0.33)=0.667\,\mathrm{fF}$$
$$C_{g,p}=1.21(0.18)(8.91)+1.21(0.32)\approx2.33\,\mathrm{fF}$$
$$C_L\approx C_{g,n}+C_{g,p}+C_{db,n}+C_{db,p}\approx2(C_{g,n}+C_{g,p})=6.00\,\mathrm{fF}$$

Con el modelo lineal de corriente por ancho usado en 1.a, ambos transistores entregan en \(V_M\) aproximadamente \(I=44.9\,\mu\mathrm{A}\). La resistencia equivalente en ese punto es \(R\approx0.9\,\mathrm{V}/44.9\,\mu\mathrm{A}=20.1\,\mathrm{k}\Omega\), de donde:

$$t_{pHL}\approx t_{pLH}\approx0.69(20.1\,\mathrm{k}\Omega)(6.00\,\mathrm{fF})\approx83\,\mathrm{ps}$$

Este retardo es una estimación RC de primer orden, no un resultado de simulación. Asume que el valor de corriente en el punto de conmutación representa la resistencia efectiva del flanco, y que las capacitancias de difusión pueden aproximarse por las de compuerta según [4]; no incluye cableado, variación de capacitancia con tensión ni formas no lineales de corriente. Por ello, se espera que el retardo SPICE difiera. La consigna requiere validar en HSPICE el circuito con una carga idéntica y reportar por separado \(tpHL\), \(tpLH\), la VTC y la corriente de cortocircuito.

Para facilitar esa comprobación se prepararon dos decks: `spice_decks/self_loaded_inverter_dc.sp` barre la entrada para obtener la VTC, el umbral medido y la corriente de alimentación en \(V_{out}=V_{DD}/2\); `spice_decks/self_loaded_inverter_tran.sp` mide \(tpHL\), \(tpLH\), \(tpd\), \(tfall\) y \(trise\) con entrada cuadrada. Ambos instancian dos inversores idénticos con \(N=4\), \(P=13.5\) y `scale=90n`, que corresponden a \(W_N=0.36\,\mu\mathrm{m}\) y \(W_P=1.215\,\mu\mathrm{m}\). Ejecutar desde `spice_decks` para que se resuelva el `.include 'min_inverter.sp'`. Las librerías se referencian desde `/mnt/vol_NFS_rh003/estudiantes/dmedina_cadence/vlsi/Hspice/lp5mos/` y deben estar disponibles en el entorno HSPICE.

#### Optimización manual
Para lograr tener la mínima diferencia entre los tiempos de propagación de subida y de bajada se modificó el deck para probar distintos ratios P/N automáticamente, este se encuentra en `fo4_ratios.sp`. Se obtuvieron las siguietes gráficas:

Para los tiempos de propagación para los distintos ratios P/N:

![tpd_ratios](https://github.com/DJosueMM/inversor_minimo_XH018/blob/main/Imagenes/FO4_opt_t.png)

De este barrido de parámetros, se concluye que el ratio P/N óptimo es de 3.4 : 1, obteniendo una diferencia de 0.21 ps. En contraste, una relación 2:1 tiene una diferencia de 10.43 ps en los tiempos de propagación. A pesar de que la relación 2:1 no es simétrica, en promedio es más rápida que la relación en el punto optimizado. La relación 2:1 tiene un tiempo de propagación promedio de 75.55 ps mientras que la relación 3.4 : 1 tiene un tiempo de propagación promedio de 87.17 ps.

Para la potencia promedio para los distintos ratios P/N:

![pwr_ratios](https://github.com/DJosueMM/inversor_minimo_XH018/blob/main/Imagenes/FO4_opt_pwr.png)

Analizando la potencia promedio, esta es directamente proporcional al ratio P/N. Para una relación 2:1 se tiene una potencia promedio de 4.94 mW meintras que para la relación en el punto de optimización se tienen 6.99 mW.

#### Optimización de hspice

Se realizó una optimización automática en hspice con el deck `fo4_opt.sp`. Se obtuvieron los siguientes datos:

|  P/λ    | bestratio | tpdr     | tpdf     | tpd      | diff     | Temperatura|
|---------|-----------|----------|----------|----------|----------|------------|
| 13.2009 | 3.3002    | 86.52 ps | 85.11 ps | 85.81 ps | 1.41 ps  | 70.00 C    |

El optimizador resultó en que el mejor ratio es de 3.3:1, con un ancho del PMOS de 13.2009 * 90nm. La diferencia entre \(tpdr\) y \(tpdf\), calculada a partir de los datos de la tabla, es de 1.41 ps.

Tanto el proceso de optimización manual como el generado por hspice convergen a resultados aproximados. El realizado manualmente llega a un punto de mayor simetría en tiempos de propagación pero el PMOS llega a ser más rápido que el NMOS, en constraste, la optimización automática encontró el mejor punto de simetría pero donde el NMOS seguía siendo más rápido que el PMOS. En términos de potencia ambas optimizaciones disipan más que un ratio 2:1 y la relación 2:1 es más rápida al tener un tpd menor que ambas optimizaciones. Por último, en términos de área se puede ver que se llegan a anchos de hasta 13.2 veces λ lo que implica un gran área para la implementación física.

Tomando todos estos parámetros en consideración, se puede concluir que valores cercanos a ratios de 2:1 y 3:1 pueden cumplir para distintos requisitos de diseño, ya sea en consumo de potencia, velocidad o simetría de las señales.

> **Pendiente para completar 1.b:** verificar/ajustar en SPICE el inversor con carga idéntica; incluir su VTC, corriente de cortocircuito y respuesta transitoria; y comparar cuantitativamente los retardos calculados (~83 ps por transición) con los simulados y con el diseño 1.a.

### Parte 2.b (continuación). Resultados preliminares de extracción de resistencia desde retardos

Los siguientes valores se conservan como resultados preliminares; falta mostrar la memoria de cálculo y confirmar que corresponden al procedimiento de la consigna 2.b.

En base a la siguiente ecuación se realizarán los cálculos de resistencia efectiva:
$tpdr = \frac{3}{2} * R_{p} * C$

|  Transistor    | Parametro | Valor (kΩ)     | 
|----------------|-----------|----------------|
| NMOS           | Rn        | 14.92          | 
| PMOS           | Rp        | 27.82          | 

### Parte 2.c. Comparación de métodos (pendiente)

Comparar estos valores con los obtenidos por descarga de capacitor (2.a), documentar ambos métodos y justificar cuál es preferible para el diseño manual.

# Bibliografía
[1] N. Weste and D. Harris, CMOS VLSI Design: A Circuits and Systems Perspective, 4 edition.
Boston: Addison-Wesley, 2010.
[2] J. Rabaey, A. Chandrakasan y B. Nikolic. Digital Integrated Circuits: A Design Perspective.
[3] Process and Device Specification XH018 - 0.18 μm Modular Mixed Signal HV CMOS, PDS-018-
13. Release 7.0.1. XFAB Semiconductor Foundries, Nov. 2017.
[4] A. Chacón Rodríguez, *Parámetros de primer orden para tecnología XFAB 0.18 μm (Bulk CMOS XH018)*, material de curso, Instituto Tecnológico de Costa Rica, 2018.
