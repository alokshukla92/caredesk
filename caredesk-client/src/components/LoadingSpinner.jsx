export default function LoadingSpinner({ size = 'md' }) {
  const sizeClass = size === 'sm' ? 'h-5 w-5' : size === 'lg' ? 'h-10 w-10' : 'h-7 w-7';
  return (
    <div className="flex items-center justify-center p-8">
      <div className={`${sizeClass} animate-spin rounded-full border-2 border-teal-200 border-t-teal-600`} />
    </div>
  );
}
