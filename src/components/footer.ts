/**
 * NEXUS-ON - Footer Component
 * Ported from backend/nexus_supervisor/public_pages_i18n.py
 */

import { Language, t } from '../../shared/i18n'

export function renderFooter(lang: Language = 'ko'): string {
  return `
    <footer>
        <p>&copy; 2026 NEXUS-ON. ${t('footer_text', lang)}</p>
        <p>${t('footer_dev', lang)}</p>
    </footer>
  `
}
