import { type Components } from "react-markdown";

export const customMarkdownComponents: Components = {
  h1: ({ node, children, ...props }) => (
    <h1
      className="text-xl font-bold mt-4 mb-2 first:mt-0 text-foreground"
      {...props}
    >
      {children}
    </h1>
  ),
  h2: ({ node, children, ...props }) => (
    <h2
      className="text-lg font-bold mt-3 mb-1.5 first:mt-0 text-foreground"
      {...props}
    >
      {children}
    </h2>
  ),
  h3: ({ node, children, ...props }) => (
    <h3
      className="text-md font-bold mt-2 mb-1 first:mt-0 text-foreground"
      {...props}
    >
      {children}
    </h3>
  ),
  h4: ({ node, children, ...props }) => (
    <h4
      className="text-base font-bold mt-2 mb-1 first:mt-0 text-foreground"
      {...props}
    >
      {children}
    </h4>
  ),
  h5: ({ node, children, ...props }) => (
    <h5
      className="text-base font-semibold mt-1.5 mb-0.5 first:mt-0 text-foreground"
      {...props}
    >
      {children}
    </h5>
  ),
  h6: ({ node, children, ...props }) => (
    <h6
      className="text-sm font-semibold mt-1 mb-0.5 first:mt-0 text-foreground"
      {...props}
    >
      {children}
    </h6>
  ),

  p: ({ node, children, ...props }) => (
    <p className="mb-2 last:mb-0 text-foreground" {...props}>
      {children}
    </p>
  ),

  ul: ({ node, children, ...props }) => (
    <ul
      className="list-disc list-inside pl-4 mb-2 last:mb-0 text-foreground"
      {...props}
    >
      {children}
    </ul>
  ),
  ol: ({ node, children, ...props }) => (
    <ol className="list-decimal pl-4 mb-2 last:mb-0 text-foreground" {...props}>
      {children}
    </ol>
  ),
  li: ({ node, children, ...props }) => (
    <li className="mb-1 text-foreground" {...props}>
      {children}
    </li>
  ),

  a: ({ node, children, href, ...props }) => (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      className="text-blue-500 hover:underline cursor-pointer"
      {...props}
    >
      {children}
    </a>
  ),

  strong: ({ node, children, ...props }) => (
    <strong className="font-bold text-foreground" {...props}>
      {children}
    </strong>
  ),
  em: ({ node, children, ...props }) => (
    <em className="italic text-foreground" {...props}>
      {children}
    </em>
  ),

  blockquote: ({ node, children, ...props }) => (
    <blockquote
      className="border-l-4 border-gray-300 pl-4 py-2 my-2 italic text-gray-600 dark:text-gray-400"
      {...props}
    >
      {children}
    </blockquote>
  ),

  code: ({ node, className, children, ...props }) => {
    return (
      <code
        className="bg-gray-200 dark:bg-gray-700 text-purple-700 dark:text-gray-300 p-0.5 rounded text-sm font-mono break-words overflow-x-auto whitespace-pre-wrap"
        {...props}
      >
        {children}
      </code>
    );
  },

  table: ({ node, children, ...props }) => (
    <table className="w-full border-collapse my-2 text-foreground" {...props}>
      {children}
    </table>
  ),
  thead: ({ node, children, ...props }) => (
    <thead className="bg-gray-100 dark:bg-gray-800" {...props}>
      {children}
    </thead>
  ),
  th: ({ node, children, ...props }) => (
    <th
      className="border border-gray-300 dark:border-gray-600 p-2 text-left font-semibold"
      {...props}
    >
      {children}
    </th>
  ),
  tbody: ({ node, children, ...props }) => <tbody {...props}>{children}</tbody>,
  tr: ({ node, children, ...props }) => (
    <tr className="even:bg-gray-50 dark:even:bg-gray-700" {...props}>
      {children}
    </tr>
  ),
  td: ({ node, children, ...props }) => (
    <td
      className="border border-gray-300 dark:border-gray-600 p-2 align-top"
      {...props}
    >
      {children}
    </td>
  ),

  hr: ({ node, ...props }) => (
    <hr
      className="my-4 border-t border-gray-300 dark:border-gray-600"
      {...props}
    />
  ),

  img: ({ node, ...props }) => (
    <img className="max-w-full h-auto rounded-lg my-2" {...props} />
  ),
};
