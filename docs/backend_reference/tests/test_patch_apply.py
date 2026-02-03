from shared.patch_apply import split_unified_diff, apply_file_patch

def test_apply_simple_patch():
    original = "a\nkeep\nend\n"
    diff = """--- a/foo.txt
+++ b/foo.txt
@@ -1,3 +1,3 @@
-a
+b
 keep
 end
"""
    p = split_unified_diff(diff)[0]
    assert p.path == "foo.txt"
    out = apply_file_patch(original, p)
    assert out == "b\nkeep\nend\n"
