def pipeline_reporte_facturacion():
    return [
        {"$match": {"yape_activo": True, "departamento": "Lima"}},

        {"$group": {
            "_id": "$tipo",
            "total_comercios": {"$sum": 1},
            "facturacion_total": {"$sum": "$monto_mensual_soles"},
            "calificacion_prom": {"$avg": "$calificacion"},
            "con_delivery": {"$sum": {"$cond": ["$acepta_delivery", 1, 0]}}
        }},

        {"$sort": {"facturacion_total": -1}},

        {"$project": {
            "tipo_comercio": "$_id",
            "total_comercios": 1,
            "facturacion_total": 1,
            "calificacion_prom": {"$round": ["$calificacion_prom", 1]},
            "con_delivery": 1,
            "_id": 0
        }}
    ]