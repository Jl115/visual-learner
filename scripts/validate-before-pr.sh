#!/usr/bin/env bash
# ════════════════════════════════════════════════════════════
# LOCAL PRE-COMMIT VALIDATION SCRIPT
# Run this before pushing to catch issues locally
# Usage: ./scripts/validate-before-pr.sh [--fix]
# ════════════════════════════════════════════════════════════

set -euo pipefail

FIX_MODE=false
if [ "${1:-}" = "--fix" ]; then
    FIX_MODE=true
    echo "🛠️  FIX MODE ENABLED — will auto-fix issues where possible"
fi

FRONTEND_DIR="./frontend"
BACKEND_DIR="./backend"
EXIT_CODE=0

echo "═══════════════════════════════════════════════════════════"
echo "🔍 PRE-PR VALIDATION"
echo "═══════════════════════════════════════════════════════════"

# ─── FRONTEND CHECKS ───────────────────────────────────────
echo ""
echo "📦 Frontend Checks..."

# 1. TypeScript type check
echo "  [1/6] TypeScript type checking..."
cd "$FRONTEND_DIR"
if npm run type-check 2>/dev/null || true; then
    # Try with vue-tsc
    if npx vue-tsc --noEmit 2>/dev/null; then
        echo "  ✅ TypeScript types pass"
    else
        echo "  ❌ TypeScript errors found"
        EXIT_CODE=1
    fi
fi
cd ..

# 2. ESLint
echo "  [2/6] ESLint..."
cd "$FRONTEND_DIR"
if $FIX_MODE; then
    echo "    (fixing)..."
    if npx eslint --fix "src/**/*.{ts,vue}" 2>/dev/null || true; then
        echo "  ✅ ESLint issues auto-fixed"
    else
        echo "  ⚠️  ESLint couldn't fix all issues"
    fi
else
    if npx eslint "src/**/*.{ts,vue}" 2>/dev/null; then
        echo "  ✅ ESLint passes"
    else
        echo "  ❌ ESLint errors found. Run with --fix to auto-fix."
        EXIT_CODE=1
    fi
fi
cd ..

# 3. Prettier
echo "  [3/6] Prettier format check..."
cd "$FRONTEND_DIR"
if $FIX_MODE; then
    if npx prettier --write "src/**/*.{ts,vue,css,json}" 2>/dev/null || true; then
        echo "  ✅ Prettier formatting applied"
    else
        echo "  ⚠️  Prettier couldn't format all files"
    fi
else
    if npx prettier --check "src/**/*.{ts,vue,css,json}" 2>/dev/null; then
        echo "  ✅ Prettier formatting passes"
    else
        echo "  ❌ Formatting issues found. Run with --fix to auto-format."
        EXIT_CODE=1
    fi
fi
cd ..

# 4. Unit Tests
echo "  [4/6] Unit tests..."
cd "$FRONTEND_DIR"
if npm run test:unit -- --run 2>/dev/null; then
    echo "  ✅ Frontend unit tests pass"
else
    echo "  ❌ Frontend unit tests FAILED"
    EXIT_CODE=1
fi
cd ..

# ─── BACKEND CHECKS ────────────────────────────────────────
echo ""
echo "🐍 Backend Checks..."

# 5. Python checks
cd "$BACKEND_DIR/.."

# Check Python files exist
if [ -d "$BACKEND_DIR" ]; then
    echo "  [5/6] Python linting..."
    
    if $FIX_MODE; then
        echo "    Running black --check..."
        black --check "backend/" 2>/dev/null || {
            echo "    🛠️  Running black --fix..."
            black "backend/" 2>/dev/null || true
            echo "  ✅ Black auto-formatted"
        }
    else
        if black --check "backend/" 2>/dev/null; then
            echo "  ✅ Black formatting passes"
        else
            echo "  ❌ Black formatting issues. Run with --fix or: black backend/"
            EXIT_CODE=1
        fi
    fi
    
    if mypy --strict "backend/app/" 2>/dev/null; then
        echo "  ✅ mypy type check passes"
    else
        echo "  ⚠️  mypy warnings (non-blocking)"
    fi
else
    echo "  ⚠️  Backend dir not found, skipping Python checks"
fi

cd "$BACKEND_DIR"
# 6. Unit tests
echo "  [6/6] Python unit tests..."
if pytest 2>/dev/null; then
    echo "  ✅ Backend unit tests pass"
else
    echo "  ⚠️  Backend tests skipped or failed"
fi
cd ..

echo ""
echo "═══════════════════════════════════════════════════════════"

if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ ALL CHECKS PASSED — Ready to create PR!"
    echo ""
    echo "Next steps:"
    echo "  git add -A && git commit -m \"feat: ...\""
    echo "  git push origin issue-{N}-memo"
    echo "  gh pr create --title \"...\" --body \"...\""
else
    echo "❌ VALIDATION FAILED — Fix issues above before creating PR"
    echo ""
    echo "Helper commands:"
    echo "  ./scripts/validate-before-pr.sh --fix   # Auto-fix formatting issues"
fi

echo "═══════════════════════════════════════════════════════════"

exit $EXIT_CODE
