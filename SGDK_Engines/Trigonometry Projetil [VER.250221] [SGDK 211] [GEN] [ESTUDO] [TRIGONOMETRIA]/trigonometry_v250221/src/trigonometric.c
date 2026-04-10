#include "trigonometric.h"

// Tabela com valores pré-calculados de Seno e Cosseno
fix16 TRIGONOMETRIC_TABLE[TABLE_SIZE] = {
    FIX16( 0.0000), FIX16( 0.0175), FIX16( 0.0349), FIX16( 0.0523), FIX16( 0.0698), FIX16( 0.0872), FIX16( 0.1045), FIX16( 0.1219), FIX16( 0.1392), FIX16( 0.1564),
	FIX16( 0.1736), FIX16( 0.1908), FIX16( 0.2079), FIX16( 0.2250), FIX16( 0.2419), FIX16( 0.2588), FIX16( 0.2756), FIX16( 0.2924), FIX16( 0.3090), FIX16( 0.3256),
	FIX16( 0.3420), FIX16( 0.3584), FIX16( 0.3746), FIX16( 0.3907), FIX16( 0.4067), FIX16( 0.4226), FIX16( 0.4384), FIX16( 0.4540), FIX16( 0.4695), FIX16( 0.4848),
	FIX16( 0.5000), FIX16( 0.5150), FIX16( 0.5299), FIX16( 0.5446), FIX16( 0.5592), FIX16( 0.5736), FIX16( 0.5878), FIX16( 0.6018), FIX16( 0.6157), FIX16( 0.6293),
	FIX16( 0.6428), FIX16( 0.6561), FIX16( 0.6691), FIX16( 0.6820), FIX16( 0.6947), FIX16( 0.7071), FIX16( 0.7193), FIX16( 0.7314), FIX16( 0.7431), FIX16( 0.7547),
	FIX16( 0.7660), FIX16( 0.7771), FIX16( 0.7880), FIX16( 0.7986), FIX16( 0.8090), FIX16( 0.8192), FIX16( 0.8290), FIX16( 0.8387), FIX16( 0.8480), FIX16( 0.8572),
	FIX16( 0.8660), FIX16( 0.8746), FIX16( 0.8829), FIX16( 0.8910), FIX16( 0.8988), FIX16( 0.9063), FIX16( 0.9135), FIX16( 0.9205), FIX16( 0.9272), FIX16( 0.9336),
	FIX16( 0.9397), FIX16( 0.9455), FIX16( 0.9511), FIX16( 0.9563), FIX16( 0.9613), FIX16( 0.9659), FIX16( 0.9703), FIX16( 0.9744), FIX16( 0.9781), FIX16( 0.9816),
	FIX16( 0.9848), FIX16( 0.9877), FIX16( 0.9903), FIX16( 0.9925), FIX16( 0.9945), FIX16( 0.9962), FIX16( 0.9976), FIX16( 0.9986), FIX16( 0.9994), FIX16( 0.9998),
	FIX16( 1.0000)
};

// FIX16ABS(x) retorna o valor absoluto de um número
fix16 FIX16ABS(fix16 x) {
    return (x < 0) ? -x : x;
}

// FIX16ATAN(x) calcula uma aproximação da função arco tangente (atan) para um valor em ponto fixo (fix16).
// Ela utiliza uma série polinomial para aproximar o valor de atan(x).
fix16 FIX16ATAN(fix16 x) {
    const fix16 a1 = FIX16( 0.999999999999999);
    const fix16 a3 = FIX16(-0.333333333333196);
    const fix16 a5 = FIX16( 0.199999975760886);
    const fix16 a7 = FIX16(-0.142356622678549);

    fix16 x2 = F16_mul(x, x);
    fix16 x3 = F16_mul(x2, x);
    fix16 x5 = F16_mul(x3, x2);
    fix16 x7 = F16_mul(x5, x2);

    return F16_mul(a1, x) + F16_mul(a3, x3) + F16_mul(a5, x5) + F16_mul(a7, x7);
}

// FIX16ATAN2(y, x) calcula o arco tangente de y/x, levando em consideração o quadrante correto, retornando o ângulo em ponto fixo.
// Ela é uma implementação do atan2, que considera os sinais de x e y para determinar o ângulo correto no círculo trigonométrico.
fix16 FIX16ATAN2(fix16 y, fix16 x) {
    if (x == 0 && y == 0)
        return 0;

    fix16 angle;
    if (FIX16ABS(x) >= FIX16ABS(y)) {
        // Quando |x| é maior ou igual a |y|, usa-se FIX16ATAN(y/x)
        angle = FIX16ATAN(F16_div(y, x));
        if (x < 0) {
            // Se x é negativo, estamos nos quadrantes II ou III
            if (y >= 0)
                angle += FIX16_PI;
            else
                angle -= FIX16_PI;
        }
    } else {
        // Quando |y| é maior que |x|, usa-se a relação com π/2
        if (y > 0) {
            angle = FIX16_HALF_PI - FIX16ATAN(F16_div(x, y));
        } else {
            angle = -FIX16_HALF_PI - FIX16ATAN(F16_div(x, y));
        }
    }

    // Normaliza o ângulo para o intervalo [0, 2π)
    if (angle < 0)
        angle += FIX16_TWO_PI;
    else if (angle >= FIX16_TWO_PI)
        angle -= FIX16_TWO_PI;

    return angle;
}

// NORMALIZE_ANGLE(a): Garante que o ângulo esteja dentro do intervalo 0-360.
fix16 NORMALIZE_ANGLE(fix16 a) {
    // Se o ângulo for maior ou igual a 360, subtrai 360 até ficar no intervalo [0, 360)
    while (a >= FIX16(360)) {
        a -= FIX16(360);
    }
    // Se o ângulo for negativo, soma 360 até ficar no intervalo [0, 360)
    while (a < FIX16(0)) {
        a += FIX16(360);
    }
    return a;
}

fix16 get_sin(int angle) {
    angle %= 360;
    if (angle < 0) angle += 360; // Garantir ângulo positivo

    int reference_angle, sign = 1;

    if (angle <= 90) { // Quadrante I
        reference_angle = angle;
    } else if (angle <= 180) { // Quadrante II
        reference_angle = 180 - angle;
    } else if (angle <= 270) { // Quadrante III
        reference_angle = angle - 180;
        sign = -1;
    } else { // Quadrante IV
        reference_angle = 360 - angle;
        sign = -1;
    }

    return sign * TRIGONOMETRIC_TABLE[reference_angle];
}

fix16 get_cos(int angle) {
    return get_sin(angle + 90); // Cosseno = Seno(ângulo + 90°)
}

// ANGLE_TO_INDEX(a) converte um ângulo em fix16 para um índice de tabela no intervalo de 0 a 359.
u16 ANGLE_TO_INDEX(fix16 a) {
    // Normaliza o ângulo para o intervalo [0, 360)
    fix16 normalizedAngle = NORMALIZE_ANGLE(a);

    // Converte o ângulo normalizado para um inteiro
    u16 angleInt = F16_toInt(normalizedAngle);

    // Mapeia o ângulo para o intervalo [0, 90]
    if (angleInt <= 90) {
        return angleInt; // Primeiro quadrante
    } else if (angleInt <= 180) {
        return 180 - angleInt; // Segundo quadrante
    } else if (angleInt <= 270) {
        return angleInt - 180; // Terceiro quadrante
    } else {
        return 360 - angleInt; // Quarto quadrante
    }
}

fix16 SIN(u16 a) {
    u16 index = ANGLE_TO_INDEX(FIX16(a)); // Obtém o índice no intervalo [0, 90]
    return TRIGONOMETRIC_TABLE[index];
}

fix16 COS(u16 a) {
    return SIN(90 - a); // Cosseno é equivalente ao seno do ângulo complementar
}

fix16 CosValor(fix16 ang)
{
    u16 angIdx = ANGLE_TO_INDEX(ang); // Índice do ângulo na tabela

    // Calcula o seno e cosseno com base no índice
    fix16 cosVal = COS(angIdx);                // Cosseno

    // Determina o sinal correto para seno e cosseno com base no quadrante
    if (ang >= FIX16(90) && ang < FIX16(180)) {
        cosVal = -cosVal;                    // Cosseno negativo no segundo quadrante
    } else if (ang >= FIX16(180) && ang < FIX16(270)) {
        cosVal = -cosVal; // Cosseno negativo no terceiro quadrante
    } else if (ang >= FIX16(270) && ang < FIX16(360)) {
        cosVal = cosVal;  // Cosseno positivo no quarto quadrante
    }

    return cosVal;
};

fix16 SinValor(fix16 ang)
{
    u16 angIdx = ANGLE_TO_INDEX(ang); // Índice do ângulo na tabela

    // Calcula o seno e cosseno com base no índice
    fix16 sinVal = TRIGONOMETRIC_TABLE[angIdx]; // Seno

    // Determina o sinal correto para seno e cosseno com base no quadrante
    if (ang >= FIX16(90) && ang < FIX16(180)) {
        sinVal = TRIGONOMETRIC_TABLE[angIdx]; // Seno positivo no segundo quadrante
    } else if (ang >= FIX16(180) && ang < FIX16(270)) {
        sinVal = -sinVal; // Seno negativo no terceiro quadrante
    } else if (ang >= FIX16(270) && ang < FIX16(360)) {
        sinVal = -sinVal; // Seno negativo no quarto quadrante
    }

    return -sinVal;
};

// GDB - TRIGONOMETRIC FIND ANGLE
fix16 TRG_FIND_ANGLE(fix16 p1x, fix16 p1y, fix16 p2x, fix16 p2y) {
	// Cálculo do ângulo
		fix16 dx = p2x - p1x;
		fix16 dy = p1y - p2y; // Y invertido

		fix16 angleRad = FIX16ATAN2(dy, dx);
		fix16 angleDeg = F16_mul(angleRad, FIX16_180_OVER_PI);
		s16 angleInDegrees = F16_toRoundedInt(angleDeg);

		// Garantir faixa 0-359
		if (angleInDegrees >= 360) angleInDegrees -= 360;
		if (angleInDegrees < 0) angleInDegrees += 360;

        // Adicione após o cálculo do angleInDegrees
		if (dx == 0) {
			angleInDegrees = (dy > 0) ? 90 : 270;
		} else if (dy == 0) {
			angleInDegrees = (dx > 0) ? 0 : 180;
		} else if (FIX16ABS(dx) == FIX16ABS(dy)) {
			if (dx > 0) {
				angleInDegrees = (dy > 0) ? 45 : 315;
			} else {
				angleInDegrees = (dy > 0) ? 135 : 225;
			}
		}

		return FIX16(angleInDegrees);
}

// GDB - MOVE X Y PIVOT ANGLE DISTANCE
void TRG_MXY_PAD(fix16 *x2, fix16 *y2, fix16 x1, fix16 y1, fix16 ang, fix16 dist) {
    u16 angIdx = ANGLE_TO_INDEX(ang); // Índice do ângulo na tabela

    // Calcula o seno e cosseno com base no índice
    fix16 sinVal = TRIGONOMETRIC_TABLE[angIdx]; // Seno
    fix16 cosVal = COS(angIdx);                // Cosseno

    // Determina o sinal correto para seno e cosseno com base no quadrante
    if (ang >= FIX16(90) && ang < FIX16(180)) {
        sinVal = TRIGONOMETRIC_TABLE[angIdx]; // Seno positivo no segundo quadrante
        cosVal = -cosVal;                    // Cosseno negativo no segundo quadrante
    } else if (ang >= FIX16(180) && ang < FIX16(270)) {
        sinVal = -sinVal; // Seno negativo no terceiro quadrante
        cosVal = -cosVal; // Cosseno negativo no terceiro quadrante
    } else if (ang >= FIX16(270) && ang < FIX16(360)) {
        sinVal = -sinVal; // Seno negativo no quarto quadrante
        cosVal = cosVal;  // Cosseno positivo no quarto quadrante
    }

    // Calcula os deslocamentos
    fix16 deslocX = F16_mul(dist, cosVal); // Projeção no eixo X
    fix16 deslocY = F16_mul(dist, sinVal); // Projeção no eixo Y

    // Atualiza as coordenadas
    *x2 = x1 + deslocX;
    *y2 = y1 - deslocY; // Inverte o eixo Y (se necessário)
}

// GDB - MOVE X Y PIVOT ANGLE DISTANCE EX
void TRG_MXY_PAD_EX(fix16 *x2, fix16 *y2, fix16 x1, fix16 y1, fix16 ang, fix16 dist, fix16 cosAdjustment, fix16 sinAdjustment) {
    u16 angIdx = ANGLE_TO_INDEX(ang); // Índice do ângulo na tabela

    // Calcula o seno e cosseno com base no índice
    fix16 sinVal = TRIGONOMETRIC_TABLE[angIdx]; // Seno
    fix16 cosVal = COS(angIdx);                // Cosseno

    // Determina o sinal correto para seno e cosseno com base no quadrante
    if (ang >= FIX16(90) && ang < FIX16(180)) {
        sinVal = TRIGONOMETRIC_TABLE[angIdx]; // Seno positivo no segundo quadrante
        cosVal = -cosVal;                    // Cosseno negativo no segundo quadrante
    } else if (ang >= FIX16(180) && ang < FIX16(270)) {
        sinVal = -sinVal; // Seno negativo no terceiro quadrante
        cosVal = -cosVal; // Cosseno negativo no terceiro quadrante
    } else if (ang >= FIX16(270) && ang < FIX16(360)) {
        sinVal = -sinVal; // Seno negativo no quarto quadrante
        cosVal = cosVal;  // Cosseno positivo no quarto quadrante
    }

    // Aplica os ajustes de escala
    sinVal = F16_mul(sinVal, sinAdjustment);
    cosVal = F16_mul(cosVal, cosAdjustment);

    // Calcula os deslocamentos
    fix16 deslocX = F16_mul(dist, cosVal); // Projeção no eixo X
    fix16 deslocY = F16_mul(dist, sinVal); // Projeção no eixo Y

    // Atualiza as coordenadas
    *x2 = x1 + deslocX;
    *y2 = y1 - deslocY; // Inverte o eixo Y (se necessário)
}
