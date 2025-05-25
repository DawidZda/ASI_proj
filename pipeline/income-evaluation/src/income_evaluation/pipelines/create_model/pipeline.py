from kedro.pipeline import node, Pipeline, pipeline  # noqa
from .nodes import validate_dataset, transform_dataset, add_new_features, train_model


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
    func=train_model,
    inputs=["income_evaluation_new_features"],
    outputs=None,
    name="train_model_node"
    )
 ])