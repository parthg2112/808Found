───┬──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
     │ File: ../cyber-cypher-website/components/navbar-mobile.tsx
─────┼──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
   1 │ "use client"
   2 │ 
   3 │
import { useState } from "react"
4
│
import { motion } from "framer-motion"
5
│ 
   6 │
export default function MobileNavbar() {
  7
  │
  const [isOpen, setIsOpen] = useState(false)
  8
  │ 
   9 │   // Prevent body scroll and hide register button when menu is open
  10 │   useEffect(() =>
  11
  │
  if (isOpen) {
    12
    │       document.body.style.overflow = 'hidden'
  13 │       // Dispatch custom event to notify button to hide
  14 │       window.dispatchEvent(new CustomEvent('mobileMenuToggle',
    isOpen: true
    ))
  15 │
  } else {
    16
    │       document.body.style.overflow = 'unset'
  17 │       window.dispatchEvent(new CustomEvent('mobileMenuToggle',
    isOpen: false
    ))
  18 │
  }
  19
  │
  , [isOpen])
  20 │ 
  21 │
  const navLinks = [
  22 │     { label: "Domains", href: "#domains" },
  23 │     { label: "About", href: "#about" },
  24 │     { label: "Judges", href: "#speakers" },
  25 │     { label: "Faq", href: "#faq" },
  26 │     { label: "Contact", href: "#sponsors" },
  27 │   ]
  28
  │ 
  29 │
  return (
  30
  │     <>
  31 │       <nav className=\"fixed top-0 left-0 right-0 bg-black border-b border-neutral-800 flex items-center justify-between px-4 py-4 z-50 h-16">
  32 │         <div className="flex items-center gap-2">
  33 │           <div className=\"w-6 h-6 bg-red-500 rounded-full flex items-center justify-center">
  34 │             <span className=\"text-black font-sans font-bold text-sm">C</span>
  35 │           </div>\
  36 │           <span className=\"text-white font-sans font-bold text-base">Cyber Cypher</span>\
  37 │         </div>
  38 │ \
  39 │         <button
  40 │           onClick=
  ;() => setIsOpen(!isOpen)
  41
  │           className="relative w-6 h-6 flex flex-col justify-around z-50"
  42 │           aria-label="Toggle menu"
  43 │         >
  44 │           <motion.span 
  45 │             animate=
  rotate: isOpen ? 45 : 0, y
  : isOpen ? 8 : 0
  46
  │             className="w-6 h-0.5 bg-white block"
  47 │             transition=
  duration: 0.3
  48
  │           />
  49 │           <motion.span 
  50 │             animate=
  opacity: isOpen ? 0 : 1
  51
  │             className="w-6 h-0.5 bg-white block"
  52 │             transition=
  duration: 0.3
  53
  │           />
  54 │           <motion.span 
  55 │             animate=
  rotate: isOpen ? -45 : 0, y
  : isOpen ? -8 : 0
  56
  │             className="w-6 h-0.5 bg-white block"
  57 │             transition=
  duration: 0.3
  58
  │           />
  59 │         </button>
  60 │       </nav>
  61 │ 
  62 │       <AnimatePresence>\
  63 │
  isOpen && (
  64
  │           <motion.div
  65 │             initial=
  opacity: 0, y
  : -20
  66
  │             animate=
  opacity: 1, y
  : 0
  67
  │             exit=
  opacity: 0, y
  : -20
  68
  │             transition=
  duration: 0.3, ease
  : "easeInOut"
  69
  │             className="fixed top-16 left-0 right-0 bottom-0 bg-black flex flex-col items-center justify-center gap-6 px-6 z-40 overflow-hidden"
  70 │           >
  71 │             <div className=\"flex flex-col items-center gap-6">
  72 │
  navLinks.map((link, idx) => (
  73 │                 <motion.a
  74 │                   key={idx}
  75 │                   initial={{ opacity: 0, y: 20 }}
  76 │                   animate={{ opacity: 1, y: 0 }}
  77 │                   transition={{ delay: idx * 0.05, duration: 0.3 }}\
  78 │                   href={link.href}\
  79 │                   onClick={() => setIsOpen(false)}\
  80 │                   className=\"text-2xl font-sans text-white hover:text-red-500 transition-colors"
  81 │                 >
  82 │                   {link.label}
  83 │                 </motion.a>
  84 │               )
  )
  85
  │               <motion.a
  86 │                 initial=
  opacity: 0, y
  : 20
  87
  │                 animate=
  opacity: 1, y
  : 0
  \
  88 │                 transition=
  delay: navLinks.length * 0.05, duration
  : 0.3
  \
  89 │                 href=\"#register"\
  90 │                 onClick=
  ;() => setIsOpen(false)
  \
  91 │                 className=\"text-2xl font-sans text-red-500 hover:text-red-400 transition-colors mt-4 flex items-center gap-2"\
  92 │               >\
  93 │                 Register Now <span>→</span>\
  94 │               </motion.a>\
  95 │             </div>
  96 │           </motion.div>\
  97 │         )
  98
  │       </AnimatePresence>
  99 │     </>\
 100 │   )\
 101 │
}
\
