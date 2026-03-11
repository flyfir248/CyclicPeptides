from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import uvicorn

app = FastAPI(
    title="CyclicPeptide API",
    description=(
        "REST API for **cyclic peptide drug design** using the `cyclicpeptide` Python package.\n\n"
        "All endpoints accept JSON bodies. Example values are pre-filled in the Swagger UI — "
        "just click **Try it out** on any endpoint."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Request / Response models ──────────────────────────────────────────────────

class SmilesRequest(BaseModel):
    smiles: str
    name: Optional[str] = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "summary": "Cyclosporin A",
                    "value": {
                        "smiles": "CC1C(=O)N(CC(=O)N(C(C(=O)NC(C(=O)N(C(C(=O)NC(C(=O)NC("
                                  "C(=O)N(C(C(=O)N(C(C(=O)N(C(C(=O)N1)CC(C)C)C)CC(C)C)C)"
                                  "CC(C)C)C)C(C)C)CC(C)C)C)C(C)O)C)C",
                        "name": "Cyclosporin A",
                    },
                },
                {
                    "summary": "Simple cyclic dipeptide",
                    "value": {
                        "smiles": "C1NC(=O)CN(C1=O)",
                        "name": "Cyclo(Gly-Gly)",
                    },
                },
            ]
        }
    }


class SequenceRequest(BaseModel):
    sequence: str
    name: Optional[str] = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "summary": "Cyclosporin A sequence",
                    "value": {
                        "sequence": "cyclo(MeBmt-Abu-MeGly-MeLeu-Val-MeLeu-Ala-D-Ala-MeLeu-MeLeu-MeVal)",
                        "name": "Cyclosporin A",
                    },
                },
                {
                    "summary": "Gramicidin S",
                    "value": {
                        "sequence": "cyclo(Val-Orn-Leu-D-Phe-Pro-Val-Orn-Leu-D-Phe-Pro)",
                        "name": "Gramicidin S",
                    },
                },
            ]
        }
    }


class PeptideEntry(BaseModel):
    name: str
    smiles: str
    sequence: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Cyclo(Gly-Gly)",
                    "smiles": "C1NC(=O)CN(C1=O)",
                    "sequence": "cyclo(Gly-Gly)",
                }
            ]
        }
    }


class BatchRequest(BaseModel):
    peptides: List[PeptideEntry]

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "summary": "Two-peptide batch",
                    "value": {
                        "peptides": [
                            {
                                "name": "Cyclo(Gly-Gly)",
                                "smiles": "C1NC(=O)CN(C1=O)",
                                "sequence": "cyclo(Gly-Gly)",
                            },
                            {
                                "name": "Gramicidin S",
                                "smiles": "CC(C)C[C@@H]1NC(=O)[C@@H]2CCCN2C(=O)"
                                          "[C@@H](Cc2ccccc2)NC(=O)[C@@H](CC(C)C)"
                                          "NC(=O)[C@@H](CCCN)NC1=O",
                                "sequence": "cyclo(Val-Orn-Leu-D-Phe-Pro-Val-Orn-Leu-D-Phe-Pro)",
                            },
                        ]
                    },
                }
            ]
        }
    }


# ── Health ─────────────────────────────────────────────────────────────────────

@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "message": "CyclicPeptide API is running"}

@app.get("/health", tags=["Health"])
def health():
    return {"status": "healthy"}

# ── PropertyAnalysis ───────────────────────────────────────────────────────────

@app.post(
    "/property/from-smiles",
    tags=["PropertyAnalysis"],
    summary="Properties from SMILES",
    responses={
        200: {
            "description": "Computed chemical/physical properties",
            "content": {
                "application/json": {
                    "example": {
                        "name": "Cyclo(Gly-Gly)",
                        "smiles": "C1NC(=O)CN(C1=O)",
                        "properties": {
                            "molecular_weight": 114.10,
                            "logP": -1.45,
                            "num_hbd": 2,
                            "num_hba": 2,
                            "tpsa": 58.36,
                        },
                    }
                }
            },
        }
    },
)
def chemical_properties_from_smiles(req: SmilesRequest):
    """
    Compute chemical/physical properties for a cyclic peptide given its **SMILES** string.

    Common properties returned include:
    - Molecular weight
    - LogP (lipophilicity)
    - H-bond donors / acceptors
    - Topological polar surface area (TPSA)
    """
    try:
        from cyclicpeptide import PropertyAnalysis as pa
        result = pa.chemial_physical_properties_from_smiles(req.smiles)
        return {"name": req.name, "smiles": req.smiles, "properties": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post(
    "/property/from-sequence",
    tags=["PropertyAnalysis"],
    summary="Properties from sequence",
    responses={
        200: {
            "description": "Computed chemical/physical properties",
            "content": {
                "application/json": {
                    "example": {
                        "name": "Gramicidin S",
                        "sequence": "cyclo(Val-Orn-Leu-D-Phe-Pro-Val-Orn-Leu-D-Phe-Pro)",
                        "properties": {
                            "molecular_weight": 1141.47,
                            "logP": 2.83,
                            "num_hbd": 6,
                            "num_hba": 10,
                            "tpsa": 214.60,
                        },
                    }
                }
            },
        }
    },
)
def chemical_properties_from_sequence(req: SequenceRequest):
    """
    Compute chemical/physical properties for a cyclic peptide given its **amino-acid sequence**.
    """
    try:
        from cyclicpeptide import PropertyAnalysis as pa
        result = pa.chemial_physical_properties_from_sequence(req.sequence)
        return {"name": req.name, "sequence": req.sequence, "properties": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ── Sequence2Structure ─────────────────────────────────────────────────────────

@app.post(
    "/structure/from-sequence",
    tags=["Sequence2Structure"],
    summary="Predict 3-D structure from sequence",
    responses={
        200: {
            "description": "Predicted structure data",
            "content": {
                "application/json": {
                    "example": {
                        "name": "Gramicidin S",
                        "sequence": "cyclo(Val-Orn-Leu-D-Phe-Pro-Val-Orn-Leu-D-Phe-Pro)",
                        "structure": {"pdb": "ATOM  ...  (truncated)", "confidence": 0.91},
                    }
                }
            },
        }
    },
)
def structure_from_sequence(req: SequenceRequest):
    """
    Predict the **3-D structure** from a cyclic peptide amino-acid sequence.

    Returns structure data (e.g., PDB-format coordinates) and a confidence score.
    """
    try:
        from cyclicpeptide import Sequence2Structure as s2s
        result = s2s.predict(req.sequence)
        return {"name": req.name, "sequence": req.sequence, "structure": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ── Structure2Sequence ─────────────────────────────────────────────────────────

@app.post(
    "/sequence/from-smiles",
    tags=["Structure2Sequence"],
    summary="Derive sequence from SMILES",
    responses={
        200: {
            "description": "Derived amino-acid sequence",
            "content": {
                "application/json": {
                    "example": {
                        "name": "Cyclo(Gly-Gly)",
                        "smiles": "C1NC(=O)CN(C1=O)",
                        "sequence": "cyclo(Gly-Gly)",
                    }
                }
            },
        }
    },
)
def sequence_from_smiles(req: SmilesRequest):
    """
    Derive the **amino-acid sequence** from a cyclic peptide SMILES string.
    """
    try:
        from cyclicpeptide import Structure2Sequence as ss
        result = ss.smiles_to_sequence(req.smiles)
        return {"name": req.name, "smiles": req.smiles, "sequence": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ── GraphAlignment ─────────────────────────────────────────────────────────────

@app.post(
    "/graph/align",
    tags=["GraphAlignment"],
    summary="Graph alignment across peptide batch",
    responses={
        200: {
            "description": "Alignment result matrix",
            "content": {
                "application/json": {
                    "example": {
                        "alignment": {
                            "score_matrix": [[1.0, 0.72], [0.72, 1.0]],
                            "aligned_pairs": [["Cyclo(Gly-Gly)", "Gramicidin S"]],
                        }
                    }
                }
            },
        }
    },
)
def graph_alignment(req: BatchRequest):
    """
    Perform **graph alignment** across a batch of cyclic peptides.

    Returns a pairwise similarity/score matrix and the best-aligned pairs.
    """
    try:
        from cyclicpeptide import GraphAlignment as ga
        entries = [(p.name, p.smiles, p.sequence) for p in req.peptides]
        result = ga.align(entries)
        return {"alignment": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ── StructureTransformer ───────────────────────────────────────────────────────

@app.post(
    "/transformer/structure",
    tags=["StructureTransformer"],
    summary="StructureTransformer on SMILES",
    responses={
        200: {
            "description": "Transformer model output",
            "content": {
                "application/json": {
                    "example": {
                        "name": "Cyclo(Gly-Gly)",
                        "smiles": "C1NC(=O)CN(C1=O)",
                        "output": {"embedding": [0.12, -0.34, 0.89, "..."], "predicted_class": "membrane-active"},
                    }
                }
            },
        }
    },
)
def structure_transformer(req: SmilesRequest):
    """
    Apply the **StructureTransformer** model to a SMILES input.

    Returns an embedding vector and any predicted structural class labels.
    """
    try:
        from cyclicpeptide import StructureTransformer as st
        result = st.transform(req.smiles)
        return {"name": req.name, "smiles": req.smiles, "output": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ── SequenceTransformer ────────────────────────────────────────────────────────

@app.post(
    "/transformer/sequence",
    tags=["SequenceTransformer"],
    summary="SequenceTransformer on amino-acid sequence",
    responses={
        200: {
            "description": "Transformer model output",
            "content": {
                "application/json": {
                    "example": {
                        "name": "Gramicidin S",
                        "sequence": "cyclo(Val-Orn-Leu-D-Phe-Pro-Val-Orn-Leu-D-Phe-Pro)",
                        "output": {"embedding": [0.45, 0.67, -0.23, "..."], "activity_score": 0.88},
                    }
                }
            },
        }
    },
)
def sequence_transformer(req: SequenceRequest):
    """
    Apply the **SequenceTransformer** model to an amino-acid sequence input.

    Returns an embedding vector and a predicted biological activity score.
    """
    try:
        from cyclicpeptide import SequenceTransformer as seqt
        result = seqt.transform(req.sequence)
        return {"name": req.name, "sequence": req.sequence, "output": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ── Batch convenience endpoint ─────────────────────────────────────────────────

@app.post(
    "/property/batch",
    tags=["PropertyAnalysis"],
    summary="Batch properties from SMILES list",
    responses={
        200: {
            "description": "Properties for each peptide in the batch",
            "content": {
                "application/json": {
                    "example": {
                        "results": [
                            {
                                "name": "Cyclo(Gly-Gly)",
                                "smiles": "C1NC(=O)CN(C1=O)",
                                "properties": {"molecular_weight": 114.10, "logP": -1.45},
                            },
                            {
                                "name": "Gramicidin S",
                                "smiles": "CC(C)C[C@@H]1NC(=O)...",
                                "properties": {"molecular_weight": 1141.47, "logP": 2.83},
                            },
                        ]
                    }
                }
            },
        }
    },
)
def batch_properties(req: BatchRequest):
    """
    Compute chemical/physical properties for a **list of cyclic peptides** (by SMILES).

    Equivalent to calling `/property/from-smiles` for each entry individually,
    but in a single round-trip.
    """
    try:
        from cyclicpeptide import PropertyAnalysis as pa
        results = []
        for p in req.peptides:
            props = pa.chemial_physical_properties_from_smiles(p.smiles)
            results.append({"name": p.name, "smiles": p.smiles, "properties": props})
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run("Main:app", host="0.0.0.0", port=8000, reload=True)