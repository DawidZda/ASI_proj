from kedro.pipeline import node, Pipeline, pipeline  # noqa
from .nodes import validate_dataset, transform_dataset, add_new_features, train_model, train_and_test_sets, balance_train_set


def create_pipeline(**kwargs) -> Pipeline:
 return pipeline([
 node(
    func=validate_dataset,
    inputs=["income_evaluation_raw"],
    outputs="income_evaluation_validated",
    name="validate_dataset_node"
    ),
 node(
    func=transform_dataset,
    inputs=["income_evaluation_validated"],
    outputs="income_evaluation_transformed",
    name="transform_dataset_node"
    ),
 node(
    func=add_new_features,
    inputs=["income_evaluation_transformed"],
    outputs="income_evaluation_new_features",
    name="add_new_features_node"
    ),
 node(
    func=train_and_test_sets,
    inputs=["income_evaluation_new_features"],
    outputs=['X_train', 'X_test', 'y_train', 'y_test'],
    name="train_and_test_sets_node"
    ),
node(
    func=balance_train_set,
    inputs=['X_train', 'y_train'],
    outputs=['X_train_balanced', 'y_train_balance'],
    name="balance_train_set_node"
    ),
 node(
    func=train_model,
    inputs=['X_train_balanced', 'X_test', 'y_train_balance', 'y_test'],
    outputs=None,
    name="train_model_node"
    )
 ])