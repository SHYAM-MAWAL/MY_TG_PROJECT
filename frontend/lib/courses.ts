export type Course = {
  id: string;
  course_title: string;
  target_url: string;
  image: string | null;
  has_image?: boolean;
  status: 'Pending' | 'Completed' | string;
  created_at: string;
};

export const API_URL =
  process.env.NEXT_PUBLIC_COURSES_API_URL?.replace(/\/$/, '') ||
  'http://127.0.0.1:8080';

/** Fast list — no base64 images in the JSON payload. */
export async function fetchCourses(limit = 200): Promise<Course[]> {
  const res = await fetch(`${API_URL}/courses?limit=${limit}&include_image=0`, {
    cache: 'no-store',
  });
  if (!res.ok) {
    throw new Error(`Courses API error: ${res.status}`);
  }
  return (await res.json()) as Course[];
}

export function courseImageUrl(course: Course): string | null {
  if (course.image && course.image.startsWith('data:image')) return course.image;
  if (course.has_image) return `${API_URL}/courses/${course.id}/image`;
  return null;
}
