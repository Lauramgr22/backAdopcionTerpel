# Evolutivo: comprobantes y aprobación de doble control

## Objetivo

Incorporar evidencia documental y segregación de funciones para reducir el riesgo operativo en pagos de alto valor.

## Historia de usuario

**Como** administrador financiero,  
**quiero** que los pagos de alto valor incluyan comprobantes y dos aprobaciones independientes,  
**para** impedir que una sola persona autorice una operación sensible.

## Alcance funcional

1. El cliente u operador podrá adjuntar comprobantes PDF o imagen.
2. El administrador configurará el umbral de doble aprobación por moneda.
3. Los pagos superiores al umbral requerirán dos aprobaciones independientes.
4. Una misma persona no podrá realizar ambas aprobaciones.
5. Cada decisión guardará actor, fecha, comentario y resultado.
6. El cliente verá el progreso sin acceder a información interna de los aprobadores.

## Criterios de aceptación

```gherkin
Escenario: pago inferior al umbral
  Dado un pago con soporte válido inferior al umbral configurado
  Cuando un operador lo aprueba
  Entonces el pago queda en estado aprobado

Escenario: pago superior al umbral
  Dado un pago superior al umbral configurado
  Cuando el primer aprobador acepta la solicitud
  Entonces el pago queda pendiente de una segunda aprobación

Escenario: segregación de funciones
  Dado un pago que ya fue aprobado por primera vez
  Cuando el mismo usuario intenta realizar la segunda aprobación
  Entonces el sistema rechaza la acción y registra el intento

Escenario: soporte obligatorio
  Dado un pago que requiere evidencia
  Cuando se intenta enviarlo sin comprobante
  Entonces el sistema informa que el soporte es obligatorio
```

## Cambios técnicos

- Crear tablas `payment_attachments`, `approval_rules` y `payment_approvals`.
- Introducir estados `first_approval` y `second_approval`.
- Añadir almacenamiento local durante el desarrollo y almacenamiento de objetos en ambientes compartidos.
- Validar tipo, tamaño y firma de los archivos; incorporar análisis antivirus.
- Autorizar cada descarga desde el backend y usar nombres internos aleatorios.
- Registrar eventos de auditoría inmutables.
- Agregar endpoints de carga y aprobación, revisando el límite inicial de cinco endpoints.

## Cambios en la interfaz

- Paso de adjuntos dentro del formulario de pago.
- Visor del comprobante para operadores.
- Línea de tiempo de aprobaciones en el detalle.
- Panel administrativo de umbrales y reglas.

## Plan sugerido

1. Diseñar migraciones y transiciones de estado.
2. Implementar almacenamiento y validación de archivos.
3. Implementar el motor de doble aprobación.
4. Construir las nuevas pantallas.
5. Añadir pruebas de autorización, concurrencia y archivos maliciosos.
6. Ejecutar un piloto con un umbral controlado.

## Fuera de alcance inicial

- Integración directa con bancos.
- Firma electrónica avanzada.
- Conciliación automática.
- Conversión entre monedas.

