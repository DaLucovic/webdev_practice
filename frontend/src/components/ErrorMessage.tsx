// role="alert" tells screen readers to announce this immediately when it appears.
// aria-live="assertive" is implied by role="alert".

interface Props {
  message: string | null;
}

export function ErrorMessage({ message }: Props) {
  if (!message) return null;

  return (
    <div className="error-box" role="alert">
      {message}
    </div>
  );
}
