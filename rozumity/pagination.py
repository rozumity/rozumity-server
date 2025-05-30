"""
Pagination serializers determine the structure of the output that should
be used for paginated responses.
"""
from django.core.paginator import InvalidPage
from rest_framework.exceptions import NotFound
from rest_framework.pagination import (
    _reverse_ordering, PageNumberPagination as DRFPageNumberPagination,
    LimitOffsetPagination as DRFLimitOffsetPagination,
    CursorPagination as DRFCursorPagination
)


class PageNumberPagination(DRFPageNumberPagination):
    async def paginate_queryset(self, queryset, request, view=None):
        self.request = request
        page_size = self.get_page_size(request)
        if not page_size:
            return None

        paginator = self.django_paginator_class(queryset, page_size)
        page_number = self.get_page_number(request, paginator)

        try:
            self.page = paginator.page(page_number)
        except InvalidPage as exc:
            msg = self.invalid_page_message.format(
                page_number=page_number, message=str(exc)
            )
            raise NotFound(msg)

        if paginator.num_pages > 1 and self.template is not None:
            # The browsable API should display pagination controls.
            self.display_page_controls = True

        return self.page


class LimitOffsetPagination(DRFLimitOffsetPagination):
    async def aget_count(self, queryset):
        try:
            return (await queryset.acount())
        except (AttributeError, TypeError):
            return len(queryset)

    async def paginate_queryset(self, queryset, request, view=None):
        self.request = request
        self.limit = self.get_limit(request)
        if self.limit is None:
            return None

        self.count = await self.aget_count(queryset)
        self.offset = self.get_offset(request)
        if self.count > self.limit and self.template is not None:
            self.display_page_controls = True

        if self.count == 0 or self.offset > self.count:
            return []
        return queryset[self.offset:self.offset + self.limit]


class CursorPagination(DRFCursorPagination):
    async def paginate_queryset(self, queryset, request, view=None):
        self.request = request
        self.page_size = self.get_page_size(request)
        if not self.page_size:
            return None

        self.base_url = request.build_absolute_uri()
        self.ordering = self.get_ordering(request, queryset, view)

        self.cursor = self.decode_cursor(request)
        if self.cursor is None:
            (offset, reverse, current_position) = (0, False, None)
        else:
            (offset, reverse, current_position) = self.cursor

        if reverse:
            queryset = queryset.order_by(*_reverse_ordering(self.ordering))
        else:
            queryset = queryset.order_by(*self.ordering)

        if current_position is not None:
            order = self.ordering[0]
            is_reversed = order.startswith('-')
            order_attr = order.lstrip('-')

            if self.cursor.reverse != is_reversed:
                kwargs = {order_attr + '__lt': current_position}
            else:
                kwargs = {order_attr + '__gt': current_position}

            queryset = queryset.filter(**kwargs)

        results = queryset[offset:offset + self.page_size + 1]
        self.page = results[:self.page_size]

        if (await results.acount()) > (await self.page.acount()):
            has_following_position = True
            num_elements = await results.acount()
            async for item in queryset[offset + num_elements:offset + num_elements + 1]:
                instance = item
                break
            following_position = self._get_position_from_instance(
                instance,
                self.ordering,
            )
        else:
            has_following_position = False
            following_position = None

        if reverse:
            self.has_next = (current_position is not None) or (offset > 0)
            self.has_previous = has_following_position
            if self.has_next:
                self.next_position = current_position
            if self.has_previous:
                self.previous_position = following_position
        else:
            self.has_next = has_following_position
            self.has_previous = (current_position is not None) or (offset > 0)
            if self.has_next:
                self.next_position = following_position
            if self.has_previous:
                self.previous_position = current_position

        if (self.has_previous or self.has_next) and self.template is not None:
            self.display_page_controls = True

        return self.page
