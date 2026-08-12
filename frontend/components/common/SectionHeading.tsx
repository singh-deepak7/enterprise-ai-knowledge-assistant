import { ReactNode } from "react";

interface Props {
  title: string;
  description: string;
  children?: ReactNode;
}

export default function SectionHeading({
  title,
  description,
  children,
}: Props) {
  return (
    <div className="mx-auto mb-12 max-w-3xl text-center">
      {children}

      <h2 className="mt-4 text-4xl font-bold">
        {title}
      </h2>

      <p className="mt-4 text-muted-foreground">
        {description}
      </p>
    </div>
  );
}