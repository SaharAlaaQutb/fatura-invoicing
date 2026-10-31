import { createBrowserRouter } from "react-router-dom";
import App from "@/app/App";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <App />,
    children: [
      { index: true, element: <div>Dashboard placeholder</div> },
      { path: "login", element: <div>Login placeholder</div> },
      { path: "invoices", element: <div>Invoices placeholder</div> },
      { path: "customers", element: <div>Customers placeholder</div> },
      { path: "products", element: <div>Products placeholder</div> },
      { path: "reports", element: <div>Reports placeholder</div> },
      { path: "settings", element: <div>Settings placeholder</div> },
    ],
  },
]);

export function Router() {
  // React Router outlet is rendered via the RouterProvider in providers.tsx
  return <div>Router placeholder</div>;
}
