import unittest
from unittest.mock import MagicMock

from pyhpo.set import HPOSet
from tests.mockontology import make_ontology


class SetMethods(unittest.TestCase):
    def test_combinations(self):
        ci = HPOSet(['term1', 'term2', 'term3'])
        res = list(ci.combinations())
        assert res == [
            ('term1', 'term2'),
            ('term1', 'term3'),
            ('term2', 'term1'),
            ('term2', 'term3'),
            ('term3', 'term1'),
            ('term3', 'term2')
        ], res

    def test_combinations_one_way(self):
        ci = HPOSet(['term1', 'term2', 'term3'])
        res = list(ci.combinations_one_way())
        assert res == [
            ('term1', 'term2'),
            ('term1', 'term3'),
            ('term2', 'term3')
        ], res


class SetInitTests(unittest.TestCase):
    def setUp(self):
        self.ontology = make_ontology()
        self.ci = HPOSet([
            term for term in self.ontology
        ])

    def test_initialization(self):
        assert len(self.ci) == len(self.ontology)

    def test_set_from_ontology(self):
        a = HPOSet.from_ontology(
            self.ontology,
            [
                'Test child level 1-1',
                'Test child level 2-1',
                'Test child level 4'
            ]
        )
        assert len(a) == 3

    def test_child_nodes(self):
        child_nodes = self.ci.child_nodes()

        assert len(child_nodes) == 2, len(child_nodes)

        assert self.ontology[1] not in child_nodes
        assert self.ontology[11] not in child_nodes
        assert self.ontology[12] not in child_nodes
        assert self.ontology[13] in child_nodes
        assert self.ontology[21] not in child_nodes
        assert self.ontology[31] not in child_nodes
        assert self.ontology[41] in child_nodes


class SetMetricsTests(unittest.TestCase):
    def setUp(self):
        self.ontology = make_ontology()
        self.ci = HPOSet([
            term for term in self.ontology
        ])

    def test_variance(self):
        i = 0
        for term in self.ontology:
            i += 1
            term.path_to_other = MagicMock(
                return_value=(i,)
            )
        res = self.ci.variance()
        assert len(res) == 4, len(res)
        assert 1 < res[0] < 7, res[0]
        assert res[1] == 1
        assert res[2] == 6, res[2]
        assert len(res[3]) == 6+5+4+3+2+1, len(res[3])

        self.ci[0].path_to_other.assert_any_call(self.ci[1])
        self.ci[0].path_to_other.assert_any_call(self.ci[2])
        self.ci[0].path_to_other.assert_any_call(self.ci[3])
        self.ci[0].path_to_other.assert_any_call(self.ci[4])
        self.ci[0].path_to_other.assert_any_call(self.ci[5])
        self.ci[0].path_to_other.assert_any_call(self.ci[6])

        self.ci[1].path_to_other.assert_any_call(self.ci[2])
        self.ci[1].path_to_other.assert_any_call(self.ci[3])
        self.ci[1].path_to_other.assert_any_call(self.ci[4])
        self.ci[1].path_to_other.assert_any_call(self.ci[5])
        self.ci[1].path_to_other.assert_any_call(self.ci[6])

        self.ci[2].path_to_other.assert_any_call(self.ci[3])
        self.ci[2].path_to_other.assert_any_call(self.ci[4])
        self.ci[2].path_to_other.assert_any_call(self.ci[5])
        self.ci[2].path_to_other.assert_any_call(self.ci[6])

        self.ci[3].path_to_other.assert_any_call(self.ci[4])
        self.ci[3].path_to_other.assert_any_call(self.ci[5])
        self.ci[3].path_to_other.assert_any_call(self.ci[6])

        self.ci[4].path_to_other.assert_any_call(self.ci[5])
        self.ci[4].path_to_other.assert_any_call(self.ci[6])

        self.ci[5].path_to_other.assert_called_once_with(self.ci[6])

    def test_no_variance(self):
        ci = HPOSet([self.ontology[1]])
        assert ci.variance() == (0, 0, 0, [])

    def test_information_content(self):
        i = 0
        for term in self.ci:
            term.information_content['omim'] = i
            term.information_content['gene'] = i*2
            i += 1
        res = self.ci.information_content()

        assert res['mean'] == 3.0
        assert res['total'] == 21
        assert res['max'] == 6
        assert res['all'] == [0, 1, 2, 3, 4, 5, 6]

        # checking default value
        assert self.ci.information_content() == res

        res = self.ci.information_content('gene')

        assert res['mean'] == 6.0
        assert res['total'] == 42
        assert res['max'] == 12
        assert res['all'] == [0, 2, 4, 6, 8, 10, 12]