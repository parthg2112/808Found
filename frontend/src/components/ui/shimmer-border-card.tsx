
import { cn } from "@/lib/utils";
import React from "react";

interface ShimmerBorderCardProps extends React.HTMLAttributes<HTMLDivElement> {
  shimmerColor?: string;
  shimmerSize?: string;
  borderRadius?: string;
  shimmerDuration?: string;
  background?: string;
  children: React.ReactNode;
}

const ShimmerBorderCard = React.forwardRef<HTMLDivElement, ShimmerBorderCardProps>(
  (
    {
      className,
      shimmerColor = "#ffffff",
      shimmerSize = "0.05em",
      shimmerDuration = "3s",
      borderRadius = "1.5rem", // Adjusted for cards
      background = "rgba(0, 0, 0, 1)",
      children,
      ...props
    },
    ref
  ) => {
    return (
      <div
        ref={ref}
        style={
          {
            "--spread": "90deg",
            "--shimmer-color": shimmerColor,
            "--radius": borderRadius,
            "--speed": shimmerDuration,
            "--cut": shimmerSize,
            "--bg": background,
          } as React.CSSProperties
        }
        className={cn(
          "group relative z-0 flex flex-col cursor-pointer overflow-hidden whitespace-nowrap border border-white/10 [background:var(--bg)] [border-radius:var(--radius)]",
          "transform-gpu transition-transform duration-300 ease-in-out active:translate-y-px",
          className
        )}
        {...props}
      >
        <div
          className={cn(
            "-z-30 blur-[2px]",
            "absolute inset-0 overflow-visible [container-type:size]"
          )}
        >
          <div className="animate-shimmer-btn-shimmer-slide absolute inset-0 h-[100cqh] [aspect-ratio:1] [border-radius:0] [mask:none]">
            <div className="animate-shimmer-btn-spin-around absolute -inset-full w-auto rotate-0 [background:conic-gradient(from_calc(270deg-(var(--spread)*0.5)),transparent_0,var(--shimmer-color)_var(--spread),transparent_var(--spread))] [translate:0_0]" />
          </div>
        </div>
        
        <div className="absolute -z-20 [background:var(--bg)] [border-radius:var(--radius)] [inset:var(--cut)]" />

        {children}
      </div>
    );
  }
);

ShimmerBorderCard.displayName = "ShimmerBorderCard";

export { ShimmerBorderCard };
