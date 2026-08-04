export default function BackgroundPattern() {
  return (
    <>
      {/* Grid */}
      <div
        className="
          absolute inset-0
          -z-20
          bg-[linear-gradient(to_right,#1f29371a_1px,transparent_1px),linear-gradient(to_bottom,#1f29371a_1px,transparent_1px)]
          bg-[size:48px_48px]
        "
      />

      {/* Glow 1 */}
      <div
        className="
          absolute
          left-1/2
          top-24
          -z-10
          h-[500px]
          w-[500px]
          -translate-x-1/2
          rounded-full
          bg-cyan-500/20
          blur-3xl
        "
      />

      {/* Glow 2 */}
      <div
        className="
          absolute
          right-20
          top-80
          -z-10
          h-[300px]
          w-[300px]
          rounded-full
          bg-blue-600/20
          blur-3xl
        "
      />
    </>
  );
}