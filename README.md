# Aplicación de Técnicas de Reinforcement Learning al Blackjack

## 1 · Introducción

### 1.1 Motivación y objetivos

### 1.2 Qué aporta el RL frente a la estrategia clásica de Blackjack

### 1.3 Estructura del documento

## 2 · Entorno Blackjack de Gymnasium

### 2.1 Definición formal del MDP
   - Espacio de estados \((\text{player sum},\text{dealer card},\text{usable ace})\)
   - Acciones { hit, stick }
   - Recompensa y episodios terminales

### 2.2 Inspección práctica (celdas del notebook con ejemplos + visualización de utils.py)

### 2.3 Hipótesis y simplificaciones adoptadas (sab=False, natural=False, etc.)

## 3 · Metodología y algoritmos de RL

### 3.1 Algoritmo A – Control Monte Carlo (First-Visit + Exploring Starts)
- Política ε‐greedy, programación tabular
- Convergencia teórica
- Esquema de experimentación (nº episodios, semilla)

### 3.2 Algoritmo B – SARSA(λ) con trazas de elegibilidad y tile coding
- Justificación del uso de λ y función aproximada (tile coding 3D)
- Ajuste de α, ε y λ
- Ventajas frente al MC puro

### 3.3 Algoritmo C – Deep Q-Network (DQN) ligero
- Arquitectura NN (3 capas densas) + experiencia repetida + target network
- Estrategias de estabilidad (Double DQN y reward clip opcionales)
- Debate sobre "overkill" en un espacio pequeño y por qué sigue siendo didáctico

### 3.4 Hiperparámetros y protocolo experimental común
- Nº episodios de entrenamiento y test
- Métricas: retorno medio por mano, % victorias, % busts
- Criterios de parada

## 4 · Resultados

### 4.1 Curvas de aprendizaje (retorno medio vs episodios)

### 4.2 Rendimiento en test independiente (10 000 manos)

### 4.3 Tabla comparativa de métricas

### 4.4 Análisis estadístico básico (IC 95 %, test t pareado)

## 5 · Discusión

### 5.1 Ventajas y desventajas de cada método en Blackjack

### 5.2 Impacto del tamaño de muestra y de la exploración

### 5.3 Limitaciones (estado discreto, sin contar conteo de cartas real, etc.)

### 5.4 Posibles mejoras (dueling DQN, policy gradients con baseline, aprendizaje offline…)

## 6 · Conclusiones
- Síntesis de hallazgos
- Recomendaciones prácticas
- Valoración del aprendizaje personal/grupal

## 7 · Trabajo futuro y reproducibilidad
- Ideas de extensión (modo "infinite deck", variación de reglas…)
- Instrucciones para ejecutar el código y reproducir resultados
- Enlace al vídeo de 1 minuto con la demo de políticas aprendidas

## 8 · Referencias bibliográficas