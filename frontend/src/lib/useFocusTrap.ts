/**
 * useFocusTrap - Sidecar/Modal용 포커스 트랩 훅
 * 
 * WCAG 2.1 AA 준수:
 * - Tab/Shift+Tab으로 포커스 순환
 * - ESC 키로 닫기
 * - 이전 포커스 복원
 * 
 * @param isOpen - 모달/사이드카 열림 상태
 * @param onClose - 닫기 콜백
 * @returns ref - 컨테이너 요소에 적용할 ref
 */

import { useEffect, useRef } from 'react';

export function useFocusTrap(isOpen: boolean, onClose: () => void) {
  const containerRef = useRef<HTMLElement>(null);
  const previousActiveElement = useRef<HTMLElement | null>(null);

  useEffect(() => {
    if (!isOpen || !containerRef.current) return;

    // 이전 포커스 저장
    previousActiveElement.current = document.activeElement as HTMLElement;

    const container = containerRef.current;
    
    // 포커스 가능한 요소 선택
    const focusableElements = container.querySelectorAll<HTMLElement>(
      'button:not([disabled]), ' +
      '[href], ' +
      'input:not([disabled]), ' +
      'select:not([disabled]), ' +
      'textarea:not([disabled]), ' +
      '[tabindex]:not([tabindex="-1"]):not([disabled])'
    );

    const firstElement = focusableElements[0];
    const lastElement = focusableElements[focusableElements.length - 1];

    // Tab 키 트랩
    const handleTab = (e: KeyboardEvent) => {
      if (e.key !== 'Tab') return;

      if (e.shiftKey) {
        // Shift + Tab: 첫 요소에서 마지막 요소로
        if (document.activeElement === firstElement) {
          e.preventDefault();
          lastElement?.focus();
        }
      } else {
        // Tab: 마지막 요소에서 첫 요소로
        if (document.activeElement === lastElement) {
          e.preventDefault();
          firstElement?.focus();
        }
      }
    };

    // ESC 키로 닫기
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        e.preventDefault();
        onClose();
      }
    };

    // 이벤트 리스너 등록
    container.addEventListener('keydown', handleTab);
    container.addEventListener('keydown', handleEscape);

    // 첫 번째 요소에 포커스
    if (firstElement) {
      firstElement.focus();
    }

    // 클린업: 포커스 복원
    return () => {
      container.removeEventListener('keydown', handleTab);
      container.removeEventListener('keydown', handleEscape);

      // 이전 포커스 복원
      if (previousActiveElement.current) {
        previousActiveElement.current.focus();
      }
    };
  }, [isOpen, onClose]);

  return containerRef;
}

/**
 * 사용 예시:
 * 
 * function Sidecar({ isOpen, onClose }: Props) {
 *   const sidecarRef = useFocusTrap(isOpen, onClose);
 * 
 *   return (
 *     <aside 
 *       ref={sidecarRef}
 *       className="sidecar" 
 *       data-open={isOpen}
 *       role="dialog"
 *       aria-modal="true"
 *       aria-labelledby="sidecar-title"
 *     >
 *       <div className="sidecar-header">
 *         <h2 id="sidecar-title">요약</h2>
 *         <button onClick={onClose} aria-label="닫기">
 *           <X size={24} />
 *         </button>
 *       </div>
 *       <div className="sidecar-content">
 *         <!-- 콘텐츠 -->
 *       </div>
 *     </aside>
 *   );
 * }
 */
