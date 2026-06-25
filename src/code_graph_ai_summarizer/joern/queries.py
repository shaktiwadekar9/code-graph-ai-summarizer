from __future__ import annotations


def joern_queries(max_items: int) -> dict[str, str]:
    """CPGQL queries used to extract repo-level graph facts."""
    return {
        "files": f"""
            cpg.file.name.dedup
              .filterNot(_.startsWith("<"))
              .take({max_items})
              .toJson
        """,
        "methods": f"""
            cpg.method
              .filterNot(_.isExternal)
              .take({max_items})
              .map(m => Map(
                "file" -> m.filename,
                "name" -> m.name,
                "fullName" -> m.fullName,
                "signature" -> m.signature,
                "line" -> m.lineNumber.getOrElse(-1).toString
              ))
              .toJson
        """,
        "types": f"""
            cpg.typeDecl
              .filterNot(_.isExternal)
              .take({max_items})
              .map(t => Map(
                "file" -> t.filename,
                "name" -> t.name,
                "fullName" -> t.fullName,
                "line" -> t.lineNumber.getOrElse(-1).toString
              ))
              .toJson
        """,
        "call_edges": f"""
            cpg.method
              .filterNot(_.isExternal)
              .take({max_items})
              .map(m => Map(
                "callerFile" -> m.filename,
                "caller" -> m.fullName,
                "callerName" -> m.name,
                "callees" -> m.callee
                  .filterNot(_.isExternal)
                  .fullName
                  .dedup
                  .take(30)
                  .l
                  .mkString("|||"),
                "externalCallees" -> m.callee
                  .filter(_.isExternal)
                  .fullName
                  .dedup
                  .take(30)
                  .l
                  .mkString("|||")
              ))
              .toJson
        """,
        "calls": f"""
            cpg.call
              .take({max_items})
              .map(c => Map(
                "file" -> c.method.filename,
                "method" -> c.method.fullName,
                "name" -> c.name,
                "code" -> c.code,
                "target" -> c.methodFullName,
                "line" -> c.lineNumber.getOrElse(-1).toString
              ))
              .toJson
        """,
        "entry_candidates": f"""
            val entryRe = "(?i).*(main|run|start|serve|handler|handle|route|controller|command|execute|process|consume|worker|app).*"

            cpg.method
              .filterNot(_.isExternal)
              .filter(m =>
                m.name.matches(entryRe) ||
                m.filename.matches(entryRe)
              )
              .take({max_items})
              .map(m => Map(
                "file" -> m.filename,
                "name" -> m.name,
                "fullName" -> m.fullName,
                "signature" -> m.signature,
                "line" -> m.lineNumber.getOrElse(-1).toString
              ))
              .toJson
        """,
        "source_sink_calls": f"""
            val dataRe = "(?i).*(request|input|read|upload|file|argv|args|getenv|env|body|param|query|write|save|insert|update|delete|execute|commit|chat|completion|generate|post|put|send|return|response).*"

            cpg.call
              .filter(c => c.name.matches(dataRe) || c.code.matches(dataRe))
              .take({max_items})
              .map(c => Map(
                "file" -> c.method.filename,
                "method" -> c.method.fullName,
                "name" -> c.name,
                "code" -> c.code,
                "target" -> c.methodFullName,
                "line" -> c.lineNumber.getOrElse(-1).toString
              ))
              .toJson
        """,
    }


def reachable_by_flows_query() -> str:
    """Optional Joern data-flow query. It may fail depending on language overlays."""
    return """
        def source = cpg.method.parameter

        def sink = cpg.call
          .name("(?i).*(write|save|insert|update|execute|chat|completion|post|put|send).*")
          .argument

        sink.reachableByFlows(source).take(40).p
    """
