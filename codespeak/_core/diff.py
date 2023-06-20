import os
from typing import Callable
from codespeak._declaration.declaration_file_service import DeclarationFileService
from codespeak._metadata import FunctionMetadata
from codespeak._metadata.digest import DeclarationDigest


def require_new_codegen(
    file_service: DeclarationFileService,
    active_digest: DeclarationDigest,
    require_deep_hash_match: bool = False,
) -> bool:
    if not file_service.does_metadata_exist():
        return True
    try:
        existing_metadata = file_service.load_metadata()
    except Exception as e:
        print("unable to load prev metadata")
        return True
    if existing_metadata is None:
        raise Exception("Metadata should exist if the file exists")
    if existing_metadata.require_execution and not existing_metadata.did_execute:
        return True
    if existing_metadata.has_tests and not existing_metadata.did_pass_tests:
        return True
    return has_function_changed(
        existing_metadata, active_digest, require_deep_hash_match
    )


def has_function_changed(
    existing_metadata: FunctionMetadata,
    active_digest: DeclarationDigest,
    require_deep_hash_match: bool = False,
):
    if require_deep_hash_match:
        return existing_metadata.declaration_digest.deep_hash != active_digest.deep_hash
    else:
        return (
            existing_metadata.declaration_digest.source_hash
            != active_digest.source_hash
        )
