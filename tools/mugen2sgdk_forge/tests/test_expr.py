"""Contrato do compilador de expressoes + VM de referencia."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from mugen2sgdk_forge.ir import expr, opcodes as O, vm  # noqa: E402

FX = O.FX
CTX = expr.Ctx({"qcf_x": 0, "holdfwd": 1},
               {"velocity": {"walk.fwd": "2.4", "run.back": "-4.5,-3.8"}, "data": {"life": "1000"}},
               {0, 200})


class Env:
    def __init__(self, **v):
        self.v = {"time": 0, "stateno": 0, "statetype": ord("S"), "ctrl": 1, "vel_x": 0}
        self.v.update(v)
        self.cmds, self.elem = set(), {}

    def trg(self, i):
        return int(self.v.get(O.TRIGGERS[i], 0) * FX)

    def trga(self, i, arg):
        return int(self.v.get(f"{O.TRIGGERS_ARG[i]}({arg // FX})", 0) * FX)

    def cmd(self, idx):
        return idx in self.cmds

    def animelemtime(self, e):
        return self.elem.get(e, -1)


def ev(text, env=None):
    ce = expr.compile_expr(text, CTX)
    assert not ce.unsupported, ce.unsupported
    return vm.run(ce.code, env or Env()) / FX


@pytest.mark.parametrize("text,val", [
    ("1 + 2 * 3", 7), ("(1 + 2) * 3", 9), ("7 / 2", 3.5), ("7 % 3", 1), ("2 ** 3", 8),
    ("!0", 1), ("-3 + 1", -2), ("1 || 0 && 0", 1), ("3 > 2 = 1", 1),
    ("ifelse(0, 5, 6)", 6), ("abs(-4)", 4), ("const(velocity.walk.fwd)", 2.4),
    ("const(velocity.run.back.y)", -3.8), ("const(data.life)", 1000),
    ("selfanimexist(200)", 1), ("selfanimexist(201)", 0),
])
def test_arith_and_constants(text, val):
    assert ev(text) == pytest.approx(val, abs=1 / FX)


def test_triggers_and_symbols():
    env = Env(stateno=210, statetype=ord("A"), time=7)
    assert ev("stateno = [200, 220]", env) == 1
    assert ev("stateno = (200, 210)", env) == 0
    assert ev("stateno != [200,210]", env) == 0
    assert ev("statetype = A", env) == 1
    assert ev("statetype != S && ctrl", env) == 1
    assert ev("timemod = 3, 1", env) == 1


def test_command_and_animelem():
    env = Env()
    env.cmds.add(0)
    env.elem = {2: 0, 3: 4}
    assert ev('command = "QCF_X"', env) == 1
    assert ev('command != "holdfwd"', env) == 1
    assert ev("animelem = 2", env) == 1
    assert ev("animelem = 3", env) == 0
    assert ev("animelem = 3, >= 2", env) == 1


def test_condition_groups_follow_mugen_rules():
    env = Env(stateno=0, ctrl=1)
    ce = expr.compile_condition(["ctrl"], {1: ["stateno = 5"], 2: ["stateno = 0", "time = 0"]}, CTX)
    assert vm.run(ce.code, env) == FX
    ce = expr.compile_condition([], {1: ["1"], 3: ["1"]}, CTX)
    assert any("fora de sequencia" in u for u in ce.unsupported)


def test_unsupported_is_reported_not_hidden():
    ce = expr.compile_expr("foo + 1", CTX)
    assert ce.unsupported == ["trigger 'foo'"]
    ce = expr.compile_expr('command = "naoexiste"', CTX)
    assert ce.unsupported and "inexistente" in ce.unsupported[0]


def test_syntax_error_is_explicit():
    with pytest.raises(expr.ExprError):
        expr.compile_expr("1 + (2", CTX)
