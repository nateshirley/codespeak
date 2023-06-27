from typing import Any, Callable, Dict, List
from codespeak._core import diff
from codespeak._declaration.codespeak_declaration import CodespeakDeclaration
from codespeak._declaration.declaration_file_service import DeclarationFileService
from codespeak._declaration.declaration_resources import DeclarationResources
from codespeak._metadata.digest import DeclarationDigest
from codespeak.inference import Inference
from codespeak.inference._inference_attributes import _InferenceAttributes
from codespeak.inference._resources import Resources
from codespeak.inference.inference_make_response import InferenceMakeResponse

"""
what do i actually want to make accessible on the inference object

in addition to what i have
- tests, resources, goal
- logic (maybe executable): None | Callable (the function that is executed when in prod)
- logic_filepath: None | str (the filepath to the logic file)
- metadata: None | dict (the metadata for the function)
- metadata_filepath: None | str (the filepath to the metadata file)
- source_code: None | str (the source code for the function)
- or I could wrap it all in a Logic class
- Logic/metadata 

"""
# resources.attach_declaration_resources


class _Inference(Inference):
    digest: DeclarationDigest

    def __init__(self, func: Callable) -> None:
        super().__init__(func)
        self.digest = DeclarationDigest.from_inputs(
            declaration_source_code=self.resources.declaration_resources.source_code,
            custom_types=self.resources.as_custom_types_str(),
        )

    def make(
        self,
        args: List[Any],
        kwargs: Dict[str, Any],
        should_execute: bool = False,
    ) -> InferenceMakeResponse:
        return self._make(
            args=args,
            kwargs=kwargs,
            should_execute=should_execute,
            digest=self.digest,
        )

    # the logic called here should probably just go in the class or in the digest
    def should_infer_new_source_code(self) -> bool:
        return diff.require_new_codegen(self.file_service, self.digest)

    @property
    def file_service(self) -> DeclarationFileService:
        return getattr(self.func, _InferenceAttributes.file_service)
