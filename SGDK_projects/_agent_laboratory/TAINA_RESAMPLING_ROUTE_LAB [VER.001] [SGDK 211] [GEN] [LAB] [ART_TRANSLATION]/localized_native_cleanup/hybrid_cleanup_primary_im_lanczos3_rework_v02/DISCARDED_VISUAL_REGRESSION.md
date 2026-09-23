# Rework v02 — discarded visual regression

Esta tentativa não é fonte, baseline nem candidata vigente.

`hybrid_cleanup_primary_im_lanczos3_rework_v02` aplicou uma remapagem ampla por
proprietário de material depois do mapa independente. O resultado achatou massas
de pele, top, cabelo e calça, degradando a leitura de volumes e aproximando a
personagem do defeito já rejeitado de redesenho blocado/genérico.

Motivo observável: regressão visual causada pela remapagem ampla, não por falha
do contrato técnico. A v03 foi refeita a partir do controle v01, preservando os
clusters estabelecidos e restringindo a recalculação à rampa do papel atual.
