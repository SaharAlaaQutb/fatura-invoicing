import { cn } from "@/shared/lib/cn";

export function Button({
  className,
  children,
  ...props
}: {
  className?: string;
  children: React.ReactNode;
} & React.ComponentPropsWithoutRef<"button">) {
  return (
    <button
      className={cn(
        "inline-flex items-center justify-center rounded-md border border-border px-3 py-2 text-sm font-medium transition-colors focus:outline-none focus:ring-2 focus-ring-primary focus:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none",
        "bg-surface hover:bg-gray-100 text-text",
        className
      )}
      {...props}
    >
      {children}
    </button>
  );
}
