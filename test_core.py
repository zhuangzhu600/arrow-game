import unittest
import sys
import os
import time
import tempfile
import json
from unittest.mock import patch

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 启用 Windows 控制台 ANSI 颜色支持
if os.name == 'nt':
    os.system('')

from src.game_data import (
    Arrow, can_fly_out, generate_random_level, calculate_stars,
    UP, DOWN, LEFT, RIGHT
)
from src import save_system

# ANSI 颜色
GREEN = '\033[92m'
RED = '\033[91m'
CYAN = '\033[96m'
YELLOW = '\033[93m'
GRAY = '\033[90m'
BOLD = '\033[1m'
RESET = '\033[0m'


# =========================================================
class TestDirections(unittest.TestCase):
    """模块 A  ·  方向常量"""

    def test_A01_direction_semantics(self):
        """A01  四个方向常量的语义正确"""
        self.assertEqual(UP, (-1, 0), "UP 应该是行减1，列不变")
        self.assertEqual(DOWN, (1, 0), "DOWN 应该是行加1，列不变")
        self.assertEqual(LEFT, (0, -1), "LEFT 应该是行不变，列减1")
        self.assertEqual(RIGHT, (0, 1), "RIGHT 应该是行不变，列加1")

    def test_A02_direction_normalized(self):
        """A02  每个方向向量的分量绝对值不超过 1"""
        for d in [UP, DOWN, LEFT, RIGHT]:
            self.assertLessEqual(abs(d[0]), 1)
            self.assertLessEqual(abs(d[1]), 1)


# =========================================================
class TestCanFlyOut(unittest.TestCase):
    """模块 B  ·  路径检测"""

    def test_B01_right_clear(self):
        """B01  向右无阻挡，可以飞出"""
        level = [Arrow(2, 2, RIGHT)]
        self.assertTrue(can_fly_out(level[0], level, 5, 5))

    def test_B02_right_blocked(self):
        """B02  向右有阻挡，不能飞出"""
        level = [Arrow(2, 2, RIGHT), Arrow(2, 4, RIGHT)]
        self.assertFalse(can_fly_out(level[0], level, 5, 5))

    def test_B03_left_clear(self):
        """B03  向左无阻挡，可以飞出"""
        level = [Arrow(2, 2, LEFT)]
        self.assertTrue(can_fly_out(level[0], level, 5, 5))

    def test_B04_left_blocked(self):
        """B04  向左有阻挡，不能飞出"""
        level = [Arrow(2, 2, LEFT), Arrow(2, 0, LEFT)]
        self.assertFalse(can_fly_out(level[0], level, 5, 5))

    def test_B05_up_clear(self):
        """B05  向上无阻挡，可以飞出"""
        level = [Arrow(2, 2, UP)]
        self.assertTrue(can_fly_out(level[0], level, 5, 5))

    def test_B06_up_blocked(self):
        """B06  向上有阻挡，不能飞出"""
        level = [Arrow(2, 2, UP), Arrow(0, 2, UP)]
        self.assertFalse(can_fly_out(level[0], level, 5, 5))

    def test_B07_down_clear(self):
        """B07  向下无阻挡，可以飞出"""
        level = [Arrow(2, 2, DOWN)]
        self.assertTrue(can_fly_out(level[0], level, 5, 5))

    def test_B08_down_blocked(self):
        """B08  向下有阻挡，不能飞出"""
        level = [Arrow(2, 2, DOWN), Arrow(4, 2, DOWN)]
        self.assertFalse(can_fly_out(level[0], level, 5, 5))

    def test_B09_edge_out_of_bounds(self):
        """B09  边缘箭头往外飞，不发生越界错误"""
        cases = [
            Arrow(0, 0, UP),
            Arrow(4, 0, DOWN),
            Arrow(0, 0, LEFT),
            Arrow(0, 4, RIGHT),
        ]
        for arrow in cases:
            try:
                self.assertTrue(can_fly_out(arrow, [arrow], 5, 5))
            except IndexError:
                self.fail(f"箭头 {arrow} 检测时发生了越界错误")

    def test_B10_multiple_blockers_only_nearest(self):
        """B10  多个同方向阻挡时，只看最近的一个"""
        level = [Arrow(2, 0, RIGHT), Arrow(2, 2, RIGHT), Arrow(2, 4, RIGHT)]
        self.assertFalse(can_fly_out(level[0], level, 5, 5))
        self.assertFalse(can_fly_out(level[1], level, 5, 5))

    def test_B11_dead_arrows_do_not_block(self):
        """B11  已飞出的箭头不构成阻挡"""
        level = [Arrow(2, 2, RIGHT), Arrow(2, 4, RIGHT)]
        level[1].alive = False
        self.assertTrue(can_fly_out(level[0], level, 5, 5))

    def test_B12_self_not_blocking(self):
        """B12  箭头自己不算自己的阻挡"""
        level = [Arrow(2, 2, RIGHT)]
        self.assertTrue(can_fly_out(level[0], level, 5, 5))


# =========================================================
class TestGenerateLevel(unittest.TestCase):
    """模块 C  ·  随机关卡生成"""

    def test_C01_arrow_count(self):
        """C01  生成的箭头数量不超过设定值且大于 0"""
        for n in [5, 10, 15]:
            level = generate_random_level(7, 7, n)
            self.assertLessEqual(len(level), n)
            self.assertGreater(len(level), 0)

    def test_C02_no_overlap(self):
        """C02  箭头位置不重叠"""
        for _ in range(10):
            level = generate_random_level(6, 6, 10)
            positions = [(a.row, a.col) for a in level]
            self.assertEqual(len(positions), len(set(positions)),
                             "存在箭头位置重叠！")

    def test_C03_always_solvable(self):
        """C03  生成的关卡必定有解（暴力验证 30 次）"""
        for _ in range(30):
            level = generate_random_level(7, 7, 12)
            remaining = level[:]
            solvable = True
            while remaining:
                found = False
                for arrow in remaining:
                    if can_fly_out(arrow, remaining, 7, 7):
                        remaining.remove(arrow)
                        found = True
                        break
                if not found:
                    solvable = False
                    break
            self.assertTrue(solvable, "随机生成的关卡存在死锁！")

    def test_C04_valid_directions(self):
        """C04  所有箭头方向都是合法值"""
        valid = {UP, DOWN, LEFT, RIGHT}
        for _ in range(10):
            level = generate_random_level(6, 6, 10)
            for arrow in level:
                self.assertIn(arrow.direction, valid)


# =========================================================
class TestSaveSystem(unittest.TestCase):
    """模块 D  ·  存档系统"""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.tmp_path = os.path.join(self.tmpdir, "test_save.json")
        self.patcher = patch.object(save_system, "get_save_path",
                                    return_value=self.tmp_path)
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()
        if os.path.exists(self.tmp_path):
            os.remove(self.tmp_path)

    def test_D01_default_save_structure(self):
        """D01  默认存档结构正确"""
        default = save_system.get_default_save()
        self.assertIn("unlocked_level", default)
        self.assertIn("stars", default)
        self.assertIn("best_times", default)
        self.assertEqual(default["unlocked_level"], 1)
        self.assertEqual(len(default["stars"]), 5)

    def test_D02_save_and_load(self):
        """D02  保存后能正确读回"""
        data = save_system.get_default_save()
        data["unlocked_level"] = 3
        data["stars"][0] = 3
        data["best_times"][0] = 12.5
        save_system.write_save(data)

        loaded = save_system.load_save()
        self.assertEqual(loaded["unlocked_level"], 3)
        self.assertEqual(loaded["stars"][0], 3)
        self.assertAlmostEqual(loaded["best_times"][0], 12.5)

    def test_D03_corrupted_save_falls_back(self):
        """D03  损坏的存档文件能回退默认值"""
        with open(self.tmp_path, "w") as f:
            f.write("{ 这不是合法的 JSON")
        loaded = save_system.load_save()
        self.assertEqual(loaded["unlocked_level"], 1)

    def test_D04_missing_fields_filled(self):
        """D04  旧版本存档缺少字段能自动补全"""
        with open(self.tmp_path, "w", encoding="utf-8") as f:
            json.dump({"unlocked_level": 2}, f)
        loaded = save_system.load_save()
        self.assertEqual(loaded["unlocked_level"], 2)
        self.assertIn("stars", loaded)
        self.assertIn("best_times", loaded)


# =========================================================
class TestCalculateStars(unittest.TestCase):
    """模块 E  ·  星级评价"""

    def test_E01_fast_no_mistake(self):
        """E01  20 秒内、0 失误，获得 3 星"""
        self.assertEqual(calculate_stars(15.0, 0), 3)
        self.assertEqual(calculate_stars(20.0, 0), 3)

    def test_E02_mid_speed_one_mistake(self):
        """E02  20~40 秒且 ≤1 失误，获得 2 星"""
        self.assertEqual(calculate_stars(30.0, 0), 2)
        self.assertEqual(calculate_stars(30.0, 1), 2)
        self.assertEqual(calculate_stars(40.0, 1), 2)

    def test_E03_slow(self):
        """E03  超过 40 秒，获得 1 星"""
        self.assertEqual(calculate_stars(50.0, 0), 1)

    def test_E04_fast_but_mistake(self):
        """E04  20 秒内但有失误，星级会降级"""
        self.assertEqual(calculate_stars(15.0, 1), 2)
        self.assertEqual(calculate_stars(15.0, 2), 1)


# =========================================================
# 美化版测试运行器
# =========================================================
class PrettyRunner:
    def __init__(self):
        self.total = 0
        self.passed = 0
        self.failed = 0
        self.errors = []
        self.current_class = None

    def run(self, suite):
        print()
        print(f"{CYAN}{'═' * 62}{RESET}")
        print(f"{CYAN}{BOLD}          一箭又一箭  ·  核心逻辑自动化测试{RESET}")
        print(f"{CYAN}{'═' * 62}{RESET}")

        start = time.time()
        self._run_suite(suite)
        elapsed = time.time() - start

        print()
        print(f"{CYAN}{'═' * 62}{RESET}")
        print(f"{BOLD}  ▎测试结果汇总{RESET}")
        print(f"{CYAN}{'─' * 62}{RESET}")
        print(f"    总计测试     {self.total}  个")
        print(f"    {GREEN}通过          {self.passed}  个{RESET}")
        if self.failed:
            print(f"    {RED}失败          {self.failed}  个{RESET}")
        else:
            print(f"    失败          0  个")
        print(f"    用时          {elapsed:.3f}  秒")
        print(f"{CYAN}{'═' * 62}{RESET}")

        if self.failed == 0:
            print(f"{GREEN}{BOLD}             ✓   全部通过{RESET}")
        else:
            print(f"{RED}{BOLD}             ✗   存在失败{RESET}")
        print(f"{CYAN}{'═' * 62}{RESET}")
        print()

        if self.errors:
            print(f"{RED}{BOLD}错误详情：{RESET}")
            for test, err in self.errors:
                print(f"\n{RED}{test}{RESET}")
                print(err)

    def _run_suite(self, suite):
        for item in suite:
            if isinstance(item, unittest.TestSuite):
                self._run_suite(item)
            else:
                self._run_test(item)

    def _run_test(self, test):
        cls = test.__class__
        cls_name = cls.__name__
        cls_doc = cls.__doc__ or cls_name

        if cls_name != self.current_class:
            self.current_class = cls_name
            print()
            print(f"  {CYAN}{BOLD}▎{cls_doc}{RESET}")

        method_doc = test._testMethodDoc or test._testMethodName
        display = method_doc.strip()

        self.total += 1

        result = unittest.TestResult()
        test(result)

        if result.wasSuccessful():
            self.passed += 1
            print(f"    {GREEN}✓{RESET}  {display}")
        else:
            self.failed += 1
            print(f"    {RED}✗{RESET}  {display}")
            for err in result.errors + result.failures:
                self.errors.append((test, err[1]))


# =========================================================
if __name__ == '__main__':
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestDirections))
    suite.addTests(loader.loadTestsFromTestCase(TestCanFlyOut))
    suite.addTests(loader.loadTestsFromTestCase(TestGenerateLevel))
    suite.addTests(loader.loadTestsFromTestCase(TestSaveSystem))
    suite.addTests(loader.loadTestsFromTestCase(TestCalculateStars))

    PrettyRunner().run(suite)