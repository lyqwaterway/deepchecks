# ----------------------------------------------------------------------------
# Copyright (C) 2021-2023 Deepchecks (https://www.deepchecks.com)
#
# This file is part of Deepchecks.
# Deepchecks is distributed under the terms of the GNU Affero General
# Public License (version 3 or later).
# You should have received a copy of the GNU Affero General Public License
# along with Deepchecks.  If not, see <http://www.gnu.org/licenses/>.
# ----------------------------------------------------------------------------
#
"""Test for the NLP WeakSegmentsPerformance check"""
import pytest
from hamcrest import assert_that, close_to, equal_to, has_items, is_in, matches_regexp

from deepchecks.nlp.checks import MetadataSegmentsPerformance, PropertySegmentsPerformance
from tests.base.utils import equal_condition_result


def test_tweet_emotion(tweet_emotion_train_test_textdata, tweet_emotion_train_test_probabilities):
    # Arrange
    _, test = tweet_emotion_train_test_textdata
    _, test_probas = tweet_emotion_train_test_probabilities
    check = MetadataSegmentsPerformance().add_condition_segments_relative_performance_greater_than()
    # Act
    result = check.run(test, probabilities=test_probas)
    condition_result = check.conditions_decision(result)

    # Assert
    assert_that(condition_result, has_items(
        equal_condition_result(is_pass=False,
                               details='Found a segment with accuracy score of 0.305 in comparison '
                               'to an average score of 0.708 in sampled data.',
                               name='The relative performance of weakest segment is greater than '
                               '80% of average model performance.')
    ))

    assert_that(result.value['avg_score'], close_to(0.708, 0.001))
    assert_that(len(result.value['weak_segments_list']), equal_to(6))
    assert_that(result.value['weak_segments_list'].iloc[0, 0], close_to(0.305, 0.01))


def test_tweet_emotion_properties(tweet_emotion_train_test_textdata, tweet_emotion_train_test_probabilities):
    # Arrange
    _, test = tweet_emotion_train_test_textdata
    _, test_probas = tweet_emotion_train_test_probabilities
    check = PropertySegmentsPerformance().add_condition_segments_relative_performance_greater_than(max_ratio_change=0.3)
    # Act
    result = check.run(test, probabilities=test_probas)
    condition_result = check.conditions_decision(result)

    # Assert
    assert_that(condition_result, has_items(
        equal_condition_result(is_pass=True,
                               details='Found a segment with accuracy score of 0.525 in comparison to an average '
                               'score of 0.708 in sampled data.',
                               name='The relative performance of weakest segment is greater than 70% of average '
                               'model performance.')
    ))

    assert_that(result.value['avg_score'], close_to(0.708, 0.001))
    assert_that(len(result.value['weak_segments_list']), close_to(33, 1))
    assert_that(result.value['weak_segments_list'].iloc[0, 0], close_to(0.525, 0.01))


def test_warning_of_n_top_columns(tweet_emotion_train_test_textdata, tweet_emotion_train_test_probabilities):
    _, test = tweet_emotion_train_test_textdata
    _, test_probas = tweet_emotion_train_test_probabilities
    property_check = PropertySegmentsPerformance(n_top_properties=3)
    metadata_check = MetadataSegmentsPerformance(n_top_columns=2)

    property_warning = 'Parameter n_top_properties is set to 3 to avoid long computation time. This means that the ' \
                       'check will run on 3 properties selected at random. If you want to run on all properties, set ' \
                       'n_top_properties to None. Alternatively, you can set parameter properties to a list of the ' \
                       'specific properties you want to run on.'

    metadata_warning = 'Parameter n_top_columns is set to 2 to avoid long computation time. This means that the ' \
                       'check will run on 2 metadata columns selected at random. If you want to run on all metadata ' \
                       'columns, set n_top_columns to None. Alternatively, you can set parameter columns to a list ' \
                       'of the specific metadata columns you want to run on.'

    # Assert
    with pytest.warns(UserWarning, match=property_warning):
        _ = property_check.run(test, probabilities=test_probas)
    with pytest.warns(UserWarning, match=metadata_warning):
        _ = metadata_check.run(test, probabilities=test_probas)


def test_multilabel_dataset(multilabel_mock_dataset_and_probabilities):
    # Arrange
    data, probabilities = multilabel_mock_dataset_and_probabilities
    assert_that(data.is_multi_label_classification(), equal_to(True))
    check = MetadataSegmentsPerformance().add_condition_segments_relative_performance_greater_than()
    # Act
    result = check.run(data, probabilities=probabilities)
    condition_result = check.conditions_decision(result)

    # Assert
    # TODO: Check why the details is not consistent
    # assert_that(condition_result, has_items(
    #     equal_condition_result(is_pass=True,
    #                            details='Found a segment with f1 macro score of 0.712 in comparison to an average '
    #                                    'score of 0.83 in sampled data.',
    #                            name='The relative performance of weakest segment is greater '
    #                                 'than 80% of average model performance.')
    # ))
    # TODO: Remove once details becomes consistent
    pat = r'Found a segment with f1 macro score of \d+.\d+ in comparison to an average score of 0.83 in sampled data.'
    assert_that(condition_result[0].details, matches_regexp(pat))
    assert_that(condition_result[0].name, equal_to('The relative performance '
                                                      'of weakest segment is greater '
                                                      'than 80% of average model '
                                                      'performance.'))

    assert_that(result.value['avg_score'], close_to(0.83, 0.001))
    assert_that(len(result.value['weak_segments_list']), is_in([5, 6]))  # TODO: check why it's not always 5
    # assert_that(result.value['weak_segments_list'].iloc[0, 0], close_to(0.695, 0.01))  # TODO:


def test_multilabel_just_dance(just_dance_train_test_textdata, just_dance_train_test_textdata_probas):
    # Arrange
    _, data = just_dance_train_test_textdata
    _, probabilities = just_dance_train_test_textdata_probas
    assert_that(data.is_multi_label_classification(), equal_to(True))

    data = data.copy(rows_to_use = range(1000))
    probabilities = probabilities[:1000, :]
    check = PropertySegmentsPerformance()

    # Act
    result = check.run(data, probabilities=probabilities)

    # Assert
    assert_that(result.value['avg_score'], close_to(0.615, 0.001))
    assert_that(len(result.value['weak_segments_list']), is_in([79, 80]))  # TODO: check why it's not always 80
    assert_that(result.value['weak_segments_list'].iloc[0, 0], close_to(0.401, 0.01))
