import React, { useState, useCallback, useMemo } from 'react';
import { cn } from '@/lib/utils'; // Utility for className merging

/**
 * ${1:ComponentName} - Professional React component
 *
 * @example
 * ```tsx
 * <${1:ComponentName}
 *   ${2:prop}="${3:value}"
 *   onAction={(data) => console.log(data)}
 * />
 * ```
 */

// ============================================================================
// TYPES
// ============================================================================

export interface ${1:ComponentName}Props {
  /** ${4:Prop description} */
  ${2:prop}?: ${5:string};

  /** Variant for different styles */
  variant?: 'primary' | 'secondary' | 'success' | 'danger';

  /** Size of the component */
  size?: 'sm' | 'md' | 'lg';

  /** Loading state */
  isLoading?: boolean;

  /** Disabled state */
  isDisabled?: boolean;

  /** Additional CSS classes */
  className?: string;

  /** Callback function */
  onAction?: (data: any) => void;

  /** Children elements */
  children?: React.ReactNode;
}

// ============================================================================
// STYLES
// ============================================================================

const variantStyles = {
  primary: 'bg-gradient-to-r from-orange-500 to-red-500 text-white hover:from-orange-600 hover:to-red-600',
  secondary: 'bg-gray-200 text-gray-900 hover:bg-gray-300',
  success: 'bg-green-500 text-white hover:bg-green-600',
  danger: 'bg-red-500 text-white hover:bg-red-600',
};

const sizeStyles = {
  sm: 'text-sm px-3 py-1.5',
  md: 'text-base px-4 py-2',
  lg: 'text-lg px-6 py-3',
};

// ============================================================================
// COMPONENT
// ============================================================================

export const ${1:ComponentName}: React.FC<${1:ComponentName}Props> = ({
  ${2:prop},
  variant = 'primary',
  size = 'md',
  isLoading = false,
  isDisabled = false,
  className,
  onAction,
  children,
}) => {
  // State
  const [state, setState] = useState<any>(null);

  // Handlers
  const handleAction = useCallback(() => {
    if (isDisabled || isLoading) return;

    onAction?.(state);
  }, [isDisabled, isLoading, state, onAction]);

  // Computed styles
  const componentStyles = useMemo(() => {
    return cn(
      'inline-flex items-center justify-center',
      'rounded-lg font-medium',
      'transition-all duration-200',
      'focus:outline-none focus:ring-2 focus:ring-offset-2',
      variantStyles[variant],
      sizeStyles[size],
      isDisabled && 'opacity-50 cursor-not-allowed',
      isLoading && 'cursor-wait',
      className
    );
  }, [variant, size, isDisabled, isLoading, className]);

  // Render
  return (
    <div className={componentStyles}>
      {isLoading ? (
        <LoadingSpinner size={size} />
      ) : (
        <>
          {children}
        </>
      )}
    </div>
  );
};

// ============================================================================
// SUB-COMPONENTS
// ============================================================================

const LoadingSpinner: React.FC<{ size: 'sm' | 'md' | 'lg' }> = ({ size }) => {
  const spinnerSize = {
    sm: 'w-4 h-4',
    md: 'w-5 h-5',
    lg: 'w-6 h-6',
  };

  return (
    <svg
      className={cn('animate-spin', spinnerSize[size])}
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
    >
      <circle
        className="opacity-25"
        cx="12"
        cy="12"
        r="10"
        stroke="currentColor"
        strokeWidth="4"
      />
      <path
        className="opacity-75"
        fill="currentColor"
        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
      />
    </svg>
  );
};

// ============================================================================
// EXPORTS
// ============================================================================

${1:ComponentName}.displayName = '${1:ComponentName}';

export default ${1:ComponentName};
