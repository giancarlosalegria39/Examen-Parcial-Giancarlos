# P4.3 — Diferencia entre Docker y Atlas

## a) ¿Cuándo usarías MongoDB en Docker en lugar de MongoDB Atlas para el equipo de Yape?

Usaría MongoDB en Docker para desarrollo local, pruebas rápidas, validación de scripts y entornos temporales donde no quiero depender de internet. También sirve para que todos los desarrolladores tengan la misma versión de MongoDB sin instalarla manualmente.

## b) ¿Qué ventaja tiene Atlas M0 sobre el contenedor Docker para el contexto universitario?

Atlas M0 permite demostrar una base de datos real en la nube, accesible desde Colab o cualquier equipo, sin configurar infraestructura local. Además, facilita mostrar la interfaz Browse Collections, usuarios, seguridad y conexión remota durante la sustentación.

## c) ¿Qué sucede con los datos del contenedor Docker si ejecutas `docker stop yape-mongo-local` y luego `docker rm yape-mongo-local`? ¿Y con los datos de Atlas?

Con `docker stop` el contenedor se detiene pero sus datos siguen dentro del contenedor. Si luego se ejecuta `docker rm`, el contenedor se elimina y los datos se pierden si no se configuró un volumen persistente. En Atlas, los datos permanecen en la nube aunque cierres tu notebook o apagues tu computadora.
