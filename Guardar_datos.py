datos_profe_max = pd.DataFrame()
datos_profe_max['año'] = curva_de_luz_agrupada_df.obs_date.dt.year
datos_profe_max['mes'] = curva_de_luz_agrupada_df.obs_date.dt.month
datos_profe_max['día'] = curva_de_luz_agrupada_df.obs_date.dt.day
datos_profe_max = pd.concat([datos_profe_max,curva_de_luz_agrupada_df[['magnitude', 'delta', 'r', 'magnitud_reducida']]], axis=1)
datos_profe_max.to_csv('Minimos_agrupados_por_dia.txt', sep='\t')