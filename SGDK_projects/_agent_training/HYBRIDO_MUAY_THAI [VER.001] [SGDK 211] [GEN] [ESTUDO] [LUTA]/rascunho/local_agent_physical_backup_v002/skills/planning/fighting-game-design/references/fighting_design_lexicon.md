# Fighting 2D Design Lexicon

Termos canonicos usados em `fighting_2d_design_contract.json` e `fighting_moveset_frame_data.json`. Apenas o sentido operacional. Conflitos com literatura externa NAO sao automaticamente absorvidos.

## Tempo

| Termo | Significado | Unidade |
|---|---|---|
| `startup_frames` | frames do input ate o primeiro frame ativo | int >= 0 |
| `active_frames` | frames durante os quais a hitbox/hurtbox esta ativa | int >= 0 |
| `recovery_frames` | frames do ultimo frame ativo ate retorno a neutro | int >= 0 |
| `on_hit_advantage_frames` | vantagem liquida em frames para o atacante no acerto | int |
| `on_block_advantage_frames` | vantagem liquida em frames para o atacante no bloqueio | int |
| `own_displacement_px` | deslocamento em pixels do atacante durante o recovery | int |
| `punish_window_frames` | janela em frames para o oponente punir um whiff | int >= 0 |
| `pushback_on_hit_px` | empurrao em pixels no acerto | int |
| `pushback_on_block_px` | empurrao em pixels no bloqueio | int |

Frame 0 e sempre o frame do input. Frame 1 e o primeiro frame de startup. Não existe frame negativo.

## Hitbox vs Hurtbox

- hitbox: regiao que causa dano
- hurtbox: regiao que recebe dano
- sem alpha blending; sem opacidade parcial. Hitbox ativa = cor cheia. Hitbox inativa = nao desenhada.
- cena de luta tem no maximo 64 sprites no VDP. Head metric advisory; validator NAO bloqueia.

## Estados e movimentos

| Categoria | Uso | Frame data obrigatorio? |
|---|---|---|
| `normal` | chain combo basico | sim, exceto system/movement |
| `command_normal` | input com direcional + botao | SIM |
| `special` | hadouken, shoryuken, etc | SIM |
| `super` | gasta meter, geralmente multi-hit | SIM |
| `throw` | agarre, ignora hitbox | SIM |
| `system` | wakeup, tech, taunt | NAO |
| `movement` | dash, jump, walk | NAO |

## Modos

| `kind` | Quem joga | Quando precisa de training_features |
|---|---|---|
| `versus` | human_vs_human | nao |
| `arcade` | human_vs_cpu | nao |
| `story` | human_vs_cpu | nao |
| `training` | human_vs_cpu | SIM (fase ready_for_aaa) |
| `survival` | human_vs_cpu | nao |
| `boss_rush` | human_vs_cpu | nao |
| `online` | human_vs_remote | nao (rollback NAO aplicavel v1) |

## Stages

| `hazard_policy` | Significado |
|---|---|
| `no_hazards` | sem hazards; ringout impossivel |
| `soft_hazards` | hazards que nao matam (ex: queda de plataforma) |
| `stage_fatality` | ringout / hazard mortal (ex: postes, espinhos) |

## Roles de personagem

| `role` | Frame data obrigatorio | `head_metric` |
|---|---|---|
| `primary` | SIM | advisory |
| `secondary` | opcional | advisory |
| `secret` | opcional | advisory |
| `boss` | SIM | XL (advisory) |
| `training_dummy` | minimo | S (advisory) |

## IP status do lore

| `ip_status` | Risco |
|---|---|
| `original` | zero |
| `homage` | baixo se nao usar nome/movimento identificavel |
| `public_domain` | zero |
| `licensed` | exige contrato anexo |

`homage` exige `ip_notes` explicando o que foi emprestado e o que foi originalizado.

## Curacao

- `unverified_secondary_text`: texto bruto copiado; `promotion_allowed=false`
- `verified_curated`: revisado por humano; `promotion_allowed=true` somente apos revisao explicita

## Subgeneros em `future_knowledge`

Estes subgeneros existem apenas como entrada do registry, NAO como especializacao ativa:

- `air_dasher` (Guilty Gear, BBTag)
- `tag` (MvC2, DBFZ)
- `platform_fighter` (Smash)
- `3d_fighter` (Tekken, VF, DOA)
- `arena_fighter` (Naruto Storm, Dissidia)

Nenhum deles tem design contract. Migracao para `active` exige: 1) curadoria humana de biblia, 2) projeto piloto com ROM, 3) aprovacao explicita.
