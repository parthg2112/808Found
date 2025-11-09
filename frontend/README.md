# 808Found Frontend

Welcome to the 808Found Frontend repository! This project powers the user interface for 808Found, a platform designed for financial analysis, backtesting, and data visualization. Built with Next.js, React, and TypeScript, it offers a rich, interactive experience for managing stock portfolios, analyzing market trends, and executing backtests.

## Features

*   **Interactive Dashboard:** A central hub for an overview of financial data and key metrics.
*   **Stock Portfolio Management:** Tools to track and manage stock holdings with real-time updates.
*   **Stock Trend Analysis:** Visualize market trends and identify potential opportunities using interactive charts and carousels.
*   **Backtesting Execution:** Configure and run backtests on historical data to validate trading strategies.
*   **Configuration Panel:** Customize application settings and backtesting parameters.
*   **Data Upload:** Seamlessly upload and manage financial datasets.
*   **Results Dashboard:** Detailed visualization and reporting of backtesting results.
*   **Modern UI Components:** Leverages Shadcn UI and custom components for a sleek, responsive, and accessible user experience.
*   **3D Data Visualization:** Utilizes `react-three/fiber` for advanced 3D rendering capabilities, potentially for complex data models or interactive elements.
*   **Theming:** Supports light and dark modes for personalized viewing.

## Technologies Used

*   **Framework:** [Next.js 16](https://nextjs.org/)
*   **Language:** [TypeScript](https://www.typescriptlang.org/)
*   **UI Library:** [React 19](https://react.dev/)
*   **Styling:** [Tailwind CSS 4](https://tailwindcss.com/)
*   **Component Library:** [Shadcn UI](https://ui.shadcn.com/) (built on Radix UI)
*   **Package Manager:** [pnpm](https://pnpm.io/)
*   **Charting:** [Recharts](https://recharts.org/)
*   **3D Graphics:** [Three.js](https://threejs.org/) with [@react-three/fiber](https://docs.pmnd.rs/react-three-fiber/getting-started/introduction)
*   **Animation:** [Framer Motion](https://www.framer.com/motion/)
*   **Form Management:** [React Hook Form](https://react-hook-form.com/) with [Zod](https://zod.dev/) for validation.

## Getting Started

To get a local copy up and running, follow these simple steps.

### Prerequisites

Make sure you have the following installed:

*   [Node.js](https://nodejs.org/en/) (LTS version recommended)
*   [pnpm](https://pnpm.io/installation)

### Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/808Found/frontend.git
    cd frontend
    ```
2.  Install pnpm dependencies:
    ```bash
    pnpm install
    ```

### Running the Development Server

To start the development server:

```bash
pnpm dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

You can start editing the page by modifying `src/app/page.tsx`. The page auto-updates as you edit the file.

### Building for Production

To build the application for production:

```bash
pnpm build
```

To start the production server:

```bash
pnpm start
```

## Project Structure

The project follows a standard Next.js application structure with a focus on modular and reusable components.

```
src/
├── app/                  # Next.js application routes and root layout
├── components/           # Reusable React components (UI, layout, pages, auth, modals, stocks, webgl)
│   ├── auth/             # Authentication related components
│   ├── layout/           # Layout specific components (e.g., dashboard layout, sidebar)
│   ├── modals/           # Reusable modal components
│   ├── pages/            # Components representing full page sections
│   ├── stocks/           # Components related to stock data and visualization
│   ├── ui/               # Shadcn UI components and custom UI elements
│   └── webgl/            # WebGL/3D related components
├── hooks/                # Custom React hooks
├── lib/                  # Utility functions and helper modules
└── ui-components/        # Additional UI components, potentially from external libraries or specific design systems
    ├── blocks/           # Larger UI blocks or sections
    ├── forgeui/          # Custom UI library/components
    └── kokonutui/        # Another custom UI library/components
```

## Contributing

Contributions are welcome! Please ensure your code adheres to the project's coding standards and conventions. For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT License](LICENSE) (Placeholder - please create a LICENSE file if not present)