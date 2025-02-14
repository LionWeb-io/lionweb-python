from abc import abstractmethod, ABC
from typing import List, Optional, TypeVar, Generic

from lionwebpython.language.annotation import Annotation
from lionwebpython.language.classifier import Classifier
from lionwebpython.model.annotation_instance import AnnotationInstance
from lionwebpython.model.classifier_instance_utils import ClassifierInstanceUtils
from lionwebpython.model.has_feature_values import HasFeatureValues
from lionwebpython.model.impl.proxy_node import ProxyNode

T = TypeVar('T', bound=Classifier)


class ClassifierInstance(ABC, Generic[T], HasFeatureValues):
    """
    Represents an instance of a Classifier.
    """

    @abstractmethod
    def get_annotations(self, annotation: Optional[Annotation] = None) -> List[AnnotationInstance]:
        """
        Returns all the annotations associated with this ClassifierInstance.
        If an annotation type is specified, returns only instances of that type.
        """
        pass

    @abstractmethod
    def add_annotation(self, instance: AnnotationInstance):
        """
        Adds an annotation instance to this ClassifierInstance.

        Raises:
            ValueError: If the specified annotation cannot be used on this instance.
        """
        pass

    @abstractmethod
    def remove_annotation(self, instance: 'AnnotationInstance'):
        """
        Removes an annotation instance from this ClassifierInstance.
        """
        pass

    @abstractmethod
    def get_id(self) -> str:
        """
        Returns the unique identifier for this ClassifierInstance.
        """
        pass

    @abstractmethod
    def get_classifier(self) -> T:
        """
        Returns the Classifier for this instance.
        """
        pass

    @abstractmethod
    def get_parent(self) -> Optional['ClassifierInstance[T]']:
        """
        Returns the immediate parent of the Node. Should be None only for root nodes.
        """
        pass

    @staticmethod
    def collect_self_and_descendants(self: 'ClassifierInstance', include_annotations: bool,
                                     result: List['ClassifierInstance']):
        """
        Collects `self` and all its descendants into `result`.
        """
        result.append(self)
        if include_annotations:
            for annotation in self.get_annotations():
                ClassifierInstance.collect_self_and_descendants(annotation, include_annotations, result)
        for child in ClassifierInstanceUtils.get_children(self):
            if not isinstance(child, ProxyNode):
                ClassifierInstance.collect_self_and_descendants(child, include_annotations, result)
