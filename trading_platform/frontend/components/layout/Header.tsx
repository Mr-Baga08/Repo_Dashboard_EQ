interface HeaderProps {
  title: string;
}

export default function Header({ title }: HeaderProps) {
  return (
    <header className="mb-8">
      <h1 className="text-3xl font-bold text-foreground">{title}</h1>
    </header>
  );
}
