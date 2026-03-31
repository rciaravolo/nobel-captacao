import { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Menu, Home, BarChart3, Settings } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger } from '@/components/ui/sheet';
import { ThemeToggle } from '@/components/ThemeToggle';
import { useAdminAuth } from '@/hooks/useAdminAuth';
import nobelLogo from '@/assets/nobel-logo.png';

const publicMenuItems = [
  { title: 'Home', path: '/', icon: Home },
  { title: 'Materiais', path: '/materiais', icon: BarChart3 },
];

const adminMenuItem = { title: 'Admin Materiais', path: '/admin/materiais', icon: Settings };

export const MobileMenu = () => {
  const [open, setOpen] = useState(false);
  const location = useLocation();
  const { isAdmin } = useAdminAuth();

  const isActive = (path: string) => location.pathname === path;
  
  // Build menu items based on user role
  const menuItems = isAdmin 
    ? [...publicMenuItems, adminMenuItem] 
    : publicMenuItems;

  return (
    <Sheet open={open} onOpenChange={setOpen}>
      <SheetTrigger asChild>
        <Button variant="ghost" size="icon" className="md:hidden">
          <Menu className="h-6 w-6" />
          <span className="sr-only">Abrir menu</span>
        </Button>
      </SheetTrigger>
      <SheetContent side="left" className="w-72 p-0">
        <SheetHeader className="border-b border-border p-4">
          <div className="flex items-center justify-between">
            <img src={nobelLogo} alt="Nobel Capital" className="h-8 w-auto" />
            <SheetTitle className="sr-only">Menu de Navegação</SheetTitle>
          </div>
        </SheetHeader>
        
        <nav className="flex flex-col p-4 gap-2">
          {menuItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              onClick={() => setOpen(false)}
              className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                isActive(item.path)
                  ? 'bg-primary text-primary-foreground font-medium'
                  : 'text-foreground hover:bg-muted'
              }`}
            >
              <item.icon className="h-5 w-5" />
              <span>{item.title}</span>
            </Link>
          ))}
        </nav>

        <div className="absolute bottom-0 left-0 right-0 border-t border-border p-4">
          <div className="flex items-center justify-between">
            <span className="text-sm text-muted-foreground">Tema</span>
            <ThemeToggle />
          </div>
        </div>
      </SheetContent>
    </Sheet>
  );
};
