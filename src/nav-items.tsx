
import { Terminal } from "lucide-react";
import Index from "./pages/Index";

export const navItems = [
  {
    title: "CLI Assistant",
    to: "/",
    icon: <Terminal className="h-4 w-4" />,
    page: <Index />,
  },
];
